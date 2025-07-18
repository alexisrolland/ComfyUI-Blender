"""Functions to manage the WebSocket connection to the ComfyUI server."""
import ast
import json
import os
from urllib.parse import urljoin, urlencode

import bpy
import websocket

from .utils import download_file, show_error_popup
from .workflow import parse_workflow_for_outputs


# Global variable to manage the WebSocket connection
WS_CONNECTION = None
WS_LISTENING = False

def connect():
    """Connect to the WebSocket server."""

    # Get the server address from addon preferences
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    server_address = addon_prefs.server_address
    client_id = addon_prefs.client_id

    # Construct WebSocket address
    url = urljoin(server_address, "/ws")
    params = {"clientId": client_id}
    server_address = f"{url}?{urlencode(params)}"

    # Replace http with ws and https with wss
    if "https://" in server_address:
        server_address = server_address.replace("https://", "wss://")
    elif "http://" in server_address:
        server_address = server_address.replace("http://", "ws://")

    # Establish the WebSocket connection
    global WS_CONNECTION
    WS_CONNECTION = websocket.WebSocket()
    WS_CONNECTION.connect(server_address)

    # Update connection status
    addon_prefs.connection_status = True

def disconnect():
    """Disconnect from the WebSocket server."""

    global WS_CONNECTION, WS_LISTENING
    WS_LISTENING = False
    if WS_CONNECTION:
        WS_CONNECTION.close()
        WS_CONNECTION = None

    # Update connection status
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.connection_status = False

def listen():
    """Listening function to receive and process messages from the WebSocket server."""

    # Get add-on preferences
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    queue = addon_prefs.queue

    # Get expected outputs from the workflow
    # outputs = parse_workflow_for_outputs(workflow)

    # Get WebSocket connection
    global WS_CONNECTION, WS_LISTENING
    WS_LISTENING = True

    # Start listening for messages
    while WS_LISTENING:
        message = WS_CONNECTION.recv()

        # Process the message
        if isinstance(message, str) and message != "":
            message = json.loads(message)
            # print(f"Received message: {message}") # Debugging

            # Check if execution is complete
            if message["type"] == "executing":
                data = message["data"]
                if "prompt_id" in data.keys() and data["prompt_id"] in queue.keys():
                    if data["node"] is None:
                        break

            # Check if the message type is executed with outputs
            if message["type"] == "executed":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    # Get outputs from the workflow
                    key = data["node"]
                    outputs = ast.literal_eval(queue[data["prompt_id"]].outputs)

                    # Check class type to retrieve only outputs for the add-on
                    if key in outputs and outputs[key]["class_type"] == "BlenderOutputSaveImage":
                        for output in data["output"]["images"]:
                            download_file(output["filename"], output["subfolder"])

                            # Add image to outputs collection
                            image = addon_prefs.outputs_collection.add()
                            image.name = os.path.join(output["subfolder"], output["filename"])
                            image.filename = output["filename"]
                            image.type = "image"

                            # Force redraw of the UI
                            for screen in bpy.data.screens:  # Iterate through all screens
                                for area in screen.areas:  # Access areas in each screen
                                    if area.type == "VIEW_3D":  # Area of the add-on panel
                                        area.tag_redraw()

            # Raise error message from ComfyUI server
            if message["type"] == "execution_error":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    queue.remove(queue.find(data["prompt_id"]))
                    error_message = data.get("exception_message", "Unknown error")

                    # Schedule popup to run on main thread
                    # Do not call the function directly since the thread is not the main thread
                    def raise_error():
                        show_error_popup(error_message)
                        return None  # Stop the timer
                    bpy.app.timers.register(raise_error, first_interval=0.0)
            
            # Remove prompt from the queue
            if message["type"] == "execution_success":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    queue.remove(queue.find(data["prompt_id"]))

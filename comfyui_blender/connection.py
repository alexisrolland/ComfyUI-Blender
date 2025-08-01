"""Functions to manage the WebSocket connection to the ComfyUI server."""
import ast
import json
import os
import time
from urllib.parse import urljoin, urlencode

import bpy
import websocket

from .utils import download_file, show_error_popup


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
    try:
        WS_CONNECTION.connect(server_address)
    except Exception as e:
        WS_CONNECTION = None
        raise e

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

    # Get WebSocket connection
    global WS_CONNECTION, WS_LISTENING
    WS_LISTENING = True

    # Start listening for messages
    while WS_LISTENING:
        try:
            message = WS_CONNECTION.recv()
        except Exception as e:
            time.sleep(1)
            connect()  # Try to reconnect
            continue

        # Process the message
        if isinstance(message, str) and message != "":
            message = json.loads(message)
            # print(f"Received message: {message}") # Debugging

            # Reset progress bar to 0 when execution starts
            if message["type"] == "execution_start":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    addon_prefs.progress_value = 0.0

            # Update progress bar with cached nodes
            if message["type"] == "execution_cached":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    workflow = ast.literal_eval(queue[data["prompt_id"]].workflow)
                    nb_nodes_total = len(workflow)
                    nb_nodes_cached = len(data["nodes"])
                    addon_prefs.progress_value = nb_nodes_cached / nb_nodes_total

            # Check if execution is complete
            if message["type"] == "executing":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    if data["node"] is None:
                        break

                    # Update progress bar with current node execution
                    workflow = ast.literal_eval(queue[data["prompt_id"]].workflow)
                    nb_nodes_total = len(workflow)
                    addon_prefs.progress_value = addon_prefs.progress_value + (1 / nb_nodes_total)

            # Check if the message type is executed with outputs
            if message["type"] == "executed":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    # Get outputs from the workflow
                    key = data["node"]
                    outputs = ast.literal_eval(queue[data["prompt_id"]].outputs)

                    # Check class type to retrieve image outputs
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

                    # Check class type to retrieve 3D outputs
                    elif key in outputs and outputs[key]["class_type"] == "BlenderOutputDownload3D":
                        for output in data["output"]["result"]:
                            subfolder, filename = output.rsplit("/", 1)  # Split the path at the last slash to get subfolder and filename
                            download_file(filename, subfolder)

                            # Add 3D model to outputs collection
                            model = addon_prefs.outputs_collection.add()
                            model.name = os.path.join(subfolder, filename)
                            model.filename = filename
                            model.type = "3d"

                            # Force redraw of the UI
                            for screen in bpy.data.screens:  # Iterate through all screens
                                for area in screen.areas:  # Access areas in each screen
                                    if area.type == "VIEW_3D":  # Area of the add-on panel
                                        area.tag_redraw()

            # Raise error message from ComfyUI server
            if message["type"] == "execution_error":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    # Reset progress and remove prompt from the queue when execution fails
                    addon_prefs.progress_value = 0.0
                    queue.remove(queue.find(data["prompt_id"]))
                    error_message = data.get("exception_message", "Unknown error")

                    # Schedule popup to run on main thread
                    # Do not call the function directly since the thread is not the main thread
                    def raise_error():
                        show_error_popup(error_message)
                        return None  # Stop the timer
                    bpy.app.timers.register(raise_error, first_interval=0.0)

            # Remove prompt from the queue when execution completes
            if message["type"] == "execution_success":
                data = message["data"]
                if data["prompt_id"] in queue.keys():
                    addon_prefs.progress_value = 1.0
                    queue.remove(queue.find(data["prompt_id"]))

"""Functions to manage the WebSocket connection to the ComfyUI server."""
import json
import websocket

import bpy

from .utils import download_image
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
    server_address = server_address.rstrip("/")
    server_address = server_address + f"/ws?clientId={client_id}"
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

def listen(workflow, prompt_id):
    """Listening function to receive and process messages from the WebSocket server."""

    # Get expected outputs from the workflow
    outputs = parse_workflow_for_outputs(workflow)

    # Get WebSocket connection
    global WS_CONNECTION, WS_LISTENING
    WS_LISTENING = True

    # Get add-on preferences
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences

    # Start listening for messages
    while WS_LISTENING:
        message = WS_CONNECTION.recv()

        # Process the message
        if isinstance(message, str) and message != "":
            message = json.loads(message)
            print(f"Received message: {message}")

            # Check number of workflows in the queue
            if message["type"] == "status":
                data = message["data"]
                addon_prefs.queue = data["status"]["exec_info"]["queue_remaining"]

            # Check if execution is complete
            if message["type"] == "executing":
                data = message["data"]
                if "prompt_id" in data.keys() and data["prompt_id"] == prompt_id:
                    if data["node"] is None:
                        break

            # Check if the message is an executed output
            if message["type"] == "executed":
                data = message["data"]
                if data["prompt_id"] == prompt_id:
                    key = data["node"]
                    if key in outputs and outputs[key]["class_type"] == "BlenderOutputSaveImage":
                        for output in data["output"]["images"]:
                            download_image(output["filename"], output["subfolder"], output["type"])

    # Close the WebSocket connection
    disconnect()

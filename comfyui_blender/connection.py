import bpy
import json
import websocket
from .utils import download_image, parse_workflow_for_outputs

# Global variable to manage the WebSocket connection
websocket_connection = None
websocket_listening = False

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
    global websocket_connection
    websocket_connection = websocket.WebSocket()
    websocket_connection.connect(server_address)

    # Update connection status
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.connection_status = True

def disconnect():
    """Disconnect from the WebSocket server."""

    global websocket_connection, websocket_listening
    websocket_listening = False
    if websocket_connection:
        websocket_connection.close()
        websocket_connection = None

    # Update connection status
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.connection_status = False

def listen(workflow, prompt_id):
    """Listening function to receive and process messages from the WebSocket server."""

    # Get expected outputs from the workflow
    outputs = parse_workflow_for_outputs(workflow)

    # Get WebSocket connection
    global websocket_connection, websocket_listening
    websocket_listening = True

    # Start listening for messages
    while websocket_listening:
        message = websocket_connection.recv()

        # Process the message
        if isinstance(message, str) and message != "":
            message = json.loads(message)
            print(f"Received message: {message}")

            # Check if execution is complete
            if message["type"] == "status":
                data = message["data"]
                bpy.context.scene.queue = data["status"]["exec_info"]["queue_remaining"]

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
                    if key in outputs.keys() and outputs[key]["class_type"] == "BlenderOutputSaveImage":
                            for output in data["output"]["images"]:
                                download_image(output["filename"], output["subfolder"], output["type"])

    # Close the WebSocket connection
    disconnect()
"""Functions to manage the WebSocket connection to the ComfyUI server, for the Krita client."""
import ast
import json
import logging
import os
import threading

import bpy
from ._vendor import websocket

from .utils import add_custom_headers, download_file, get_websocket_url


log = logging.getLogger("comfyui_blender")


# Global variable to manage the secondary WebSocket connection
# The secondary connection is used to sync outputs from Krita AI Diffusion
WS_CONNECTION_KRITA = None
WS_LISTENER_THREAD_KRITA = None


def connect():
    """Connect to the WebSocket server."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    client_id = addon_prefs.krita_client_id

    # Construct WebSocket address
    params = {"clientId": client_id}
    headers = add_custom_headers()
    url = get_websocket_url("/ws", params=params)

    # Check if the connection request is for Blender or Krita AI Diffusion
    global WS_CONNECTION_KRITA, WS_LISTENER_THREAD_KRITA
    WS_CONNECTION_KRITA = websocket.WebSocket()
    try:
        # Establish the WebSocket connection
        log.debug(f"Create WebSocket connection with server address: {url}")
        WS_CONNECTION_KRITA.connect(url, headers=headers)
        log.debug(f"WebSocket connection established: {WS_CONNECTION_KRITA}")

        # Start the WebSocket listener in a separate thread
        WS_LISTENER_THREAD_KRITA = threading.Thread(target=listen, daemon=True)
        WS_LISTENER_THREAD_KRITA.start()

        # Update connection status
        # And force refresh of the current workflow to reload inputs that need to query the ComfyUI server
        # For instance Load Checkpoint, Load Diffusion Model, Load LoRA...
        addon_prefs.krita_connection_status = True
        addon_prefs.workflow = addon_prefs.workflow

    except Exception as e:
        WS_CONNECTION_KRITA = None
        WS_LISTENER_THREAD_KRITA = None
        addon_prefs.krita_connection_status = False
        raise e


def disconnect():
    """Disconnect from the WebSocket server."""

    # Terminate the listening thread
    global WS_LISTENER_THREAD_KRITA
    if WS_LISTENER_THREAD_KRITA:
        if WS_LISTENER_THREAD_KRITA != threading.current_thread():
            log.debug(f"Terminating listening thread: {WS_LISTENER_THREAD_KRITA}")
            WS_LISTENER_THREAD_KRITA.join(timeout=1.0)
            WS_LISTENER_THREAD_KRITA = None
            log.debug(f"Listening thread terminated")

    # Close the WebSocket connection
    global WS_CONNECTION_KRITA
    if WS_CONNECTION_KRITA:
        log.debug(f"Closing WebSocket connection: {WS_CONNECTION_KRITA}")
        WS_CONNECTION_KRITA.close()
        WS_CONNECTION_KRITA = None
        log.debug(f"WebSocket connection closed")

    # Update connection status
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.krita_connection_status = False


def listen():
    """
    Listening function to receive and process messages from the WebSocket server.
    More specifically for Krita AI Diffusion synchronization.
    """

    # Get project settings
    project_settings = bpy.context.scene.comfyui_project_settings
    krita_outputs_collection = project_settings.krita_outputs_collection

    # Start listening for messages
    global WS_CONNECTION_KRITA, WS_LISTENER_THREAD_KRITA
    while WS_LISTENER_THREAD_KRITA:
        try:
            message = WS_CONNECTION_KRITA.recv()
        except Exception as e:
            disconnect()  # The disconnect function will also set WS_LISTENER_THREAD to None
            log.error(f"WebSocket connection interrupted: {e}")
            continue

        # Process the message
        if isinstance(message, str) and message != "":
            message = json.loads(message)
            data = message["data"]
            log.debug(f"Received websocket message: {message}")

            # Check if the message type is executed with outputs
            if message["type"] == "executed":
                # Check output type to retrieve 3D outputs
                if "3d" in data["output"]:
                    for output in data["output"]["3d"]:
                        download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                        # Schedule adding 3D model to outputs collection on main thread
                        def add_3d_output(output=output):
                            model = krita_outputs_collection.add()
                            model.name = output["filename"]
                            model.filepath = os.path.join(output["subfolder"], output["filename"])
                            model.type = "3d"

                        # Call function to add output to collection
                        bpy.app.timers.register(add_3d_output, first_interval=0.0)
                    
                    # Force redraw of the UI
                    for screen in bpy.data.screens:
                        for area in screen.areas:
                            if area.type == "VIEW_3D":
                                area.tag_redraw()

                # Check output type to retrieve image outputs
                if "images" in data["output"]:
                    for output in data["output"]["images"]:
                        download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                        # Schedule adding output to collection on main thread
                        def add_image_output(output=output):
                            image = krita_outputs_collection.add()
                            image.name = output["filename"]
                            image.filepath = os.path.join(output["subfolder"], output["filename"])
                            image.type = "image"
                            return None

                        # Call function to add output to collection
                        bpy.app.timers.register(add_image_output, first_interval=0.0)

                    # Force redraw of the UI
                    for screen in bpy.data.screens:
                        for area in screen.areas:
                            if area.type == "VIEW_3D":
                                area.tag_redraw()

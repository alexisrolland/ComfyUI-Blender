"""Functions to manage the WebSocket connection to the ComfyUI server."""
import ast
import json
import logging
import os
import threading

import bpy
from ._vendor import websocket

from .utils import add_custom_headers, download_file, get_websocket_url


log = logging.getLogger("comfyui_blender")


# Global variable to manage the WebSocket connection
WS_CONNECTION = None
WS_LISTENER_THREAD = None


def connect():
    """Connect to the WebSocket server."""

    # Get the server address from addon preferences
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    client_id = addon_prefs.client_id

    # Construct WebSocket address
    params = {"clientId": client_id}
    headers = add_custom_headers()
    url = get_websocket_url("/ws", params=params)

    global WS_CONNECTION, WS_LISTENER_THREAD
    WS_CONNECTION = websocket.WebSocket()
    try:
        # Establish the WebSocket connection
        log.debug(f"Create WebSocket connection with server address: {url}")
        WS_CONNECTION.connect(url, headers=headers)
        log.debug(f"WebSocket connection established: {WS_CONNECTION}")

        # Start the WebSocket listener in a separate thread
        WS_LISTENER_THREAD = threading.Thread(target=listen, daemon=True)
        WS_LISTENER_THREAD.start()

        # Update connection status
        # And force refresh of the current workflow to reload inputs that need to query the ComfyUI server
        # For instance Load Checkpoint, Load Diffusion Model, Load LoRA...
        addon_prefs.connection_status = True
        addon_prefs.workflow = addon_prefs.workflow

    except Exception as e:
        WS_CONNECTION = None
        WS_LISTENER_THREAD = None
        addon_prefs.connection_status = False
        raise e


def disconnect():
    """Disconnect from the WebSocket server."""

    # Terminate the listening thread
    global WS_LISTENER_THREAD
    if WS_LISTENER_THREAD:
        if WS_LISTENER_THREAD != threading.current_thread():
            log.debug(f"Terminating listening thread: {WS_LISTENER_THREAD}")
            WS_LISTENER_THREAD.join(timeout=1.0)
            WS_LISTENER_THREAD = None
            log.debug(f"Listening thread terminated")

    # Close the WebSocket connection
    global WS_CONNECTION
    if WS_CONNECTION:
        log.debug(f"Closing WebSocket connection: {WS_CONNECTION}")
        WS_CONNECTION.close()
        WS_CONNECTION = None
        log.debug(f"WebSocket connection closed")

    # Update connection status
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.connection_status = False


def listen():
    """Listening function to receive and process messages from the WebSocket server."""

    # Get add-on preferences
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    queue = addon_prefs.queue

    # Get project settings
    project_settings = bpy.context.scene.comfyui_project_settings
    outputs_collection = project_settings.outputs_collection

    # Start listening for messages
    global WS_CONNECTION, WS_LISTENER_THREAD
    while WS_LISTENER_THREAD:
        try:
            message = WS_CONNECTION.recv()
        except Exception as e:
            disconnect()  # The disconnect function will also set WS_LISTENER_THREAD to None
            log.error(f"WebSocket connection interrupted: {e}")
            continue

        # Process the message
        if isinstance(message, str) and message != "":
            message = json.loads(message)
            data = message["data"]
            log.debug(f"Received websocket message: {message}")

            # Filter on prompts that are specific to the client
            if "prompt_id" in data.keys():
                if data["prompt_id"] in queue.keys():

                    # Reset progress bar to 0 when execution starts
                    if message["type"] == "execution_start":
                        queue[data["prompt_id"]].status = message["type"]
                        workflow = ast.literal_eval(queue[data["prompt_id"]].workflow)
                        queue[data["prompt_id"]].total_nb_nodes = len(workflow)
                        addon_prefs.progress_value = 0.0

                    # Update cached nodes
                    if message["type"] == "execution_cached":
                        queue[data["prompt_id"]].status = message["type"]
                        queue[data["prompt_id"]].nb_nodes_cached = len(data["nodes"])

                    # Check if execution is complete
                    if message["type"] == "executing":
                        queue[data["prompt_id"]].status = message["type"]
                        if data["node"] is None:
                            break

                    # Check if the message type is executed with outputs
                    if message["type"] == "executed":
                        queue[data["prompt_id"]].status = message["type"]

                        # Get outputs from the workflow
                        key = data["node"]
                        outputs = ast.literal_eval(queue[data["prompt_id"]].outputs)

                        # Check class type to retrieve 3D outputs
                        if key in outputs and outputs[key]["class_type"] == "BlenderOutputDownload3D":
                            for output in data["output"]["3d"]:
                                download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                                # Schedule adding 3D model to outputs collection on main thread
                                def add_3d_output(output=output):
                                    model = outputs_collection.add()
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

                        # Check class type to retrieve 3D outputs
                        elif key in outputs and outputs[key]["class_type"] == "BlenderOutputSaveGlb":
                            for output in data["output"]["3d"]:
                                download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                                # Schedule adding 3D model to outputs collection on main thread
                                def add_3d_output(output=output):
                                    model = outputs_collection.add()
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

                        # Check class type to retrieve image outputs
                        elif key in outputs and outputs[key]["class_type"] == "BlenderOutputSaveImage":
                            for output in data["output"]["images"]:
                                download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                                # Schedule adding output to collection on main thread
                                def add_image_output(output=output):
                                    image = outputs_collection.add()
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

                    # Raise error message from ComfyUI server
                    if message["type"] == "execution_error":
                        # Reset progress and remove prompt from the queue when execution fails
                        queue.remove(queue.find(data["prompt_id"]))
                        addon_prefs.progress_value = 0.0
                        error_message = data.get("exception_message", "Unknown error")
                        error_message = f"Execution error from ComfyUI server: {error_message}"

                        # Schedule popup to run on main thread
                        # Do not call the function directly since the thread is not the main thread
                        def raise_error():
                            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                            return None  # Stop the timer

                        # Call function to raise error popup
                        bpy.app.timers.register(raise_error, first_interval=0.0)

                    # Reset progress and remove prompt from the queue when execution is interrupted
                    if message["type"] == "execution_interrupted":
                        queue.remove(queue.find(data["prompt_id"]))
                        addon_prefs.progress_value = 0.0

                    # Remove prompt from the queue when execution completes
                    if message["type"] == "execution_success":
                        queue.remove(queue.find(data["prompt_id"]))
                        addon_prefs.progress_value = 1.0

                    # Update progress bar
                    if message["type"] == "progress_state":
                        # Percentage of progress contribution per node
                        total_nb_nodes = queue[data["prompt_id"]].get("total_nb_nodes", 0)
                        nb_nodes_cached = queue[data["prompt_id"]].get("nb_nodes_cached", 0)
                        nb_nodes_to_execute = total_nb_nodes - nb_nodes_cached
                        node_contribution = 100 / nb_nodes_to_execute if nb_nodes_to_execute > 0 else 100

                        # Get progress from executing nodes
                        workflow_progress = 0
                        for key, node in data["nodes"].items():
                            node_progress = node["value"] / node["max"] * node_contribution
                            workflow_progress += node_progress

                        # Update progress value
                        addon_prefs.progress_value = workflow_progress / 100.0

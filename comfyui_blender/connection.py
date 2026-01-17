"""Functions to manage the WebSocket connection to the ComfyUI server."""
import ast
import json
import logging
import os
import re
import threading

import bpy
import requests
from ._vendor import websocket

from .utils import (
    add_custom_headers,
    download_file,
    get_filepath,
    get_outputs_folder,
    get_server_url,
    get_websocket_url
)


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
        if addon_prefs.workflow:
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

    # Update connection status and force refresh of the workflow panel
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.connection_status = False
    if addon_prefs.workflow:
        addon_prefs.workflow = addon_prefs.workflow


def listen():
    """Listening function to receive and process messages from the WebSocket server."""

    # Get add-on preferences
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    prompts_collection = addon_prefs.prompts_collection

    # Get project settings
    project_settings = bpy.context.scene.comfyui_project_settings
    outputs_collection = project_settings.outputs_collection

    # Start listening for messages
    global WS_CONNECTION, WS_LISTENER_THREAD
    while WS_LISTENER_THREAD and WS_CONNECTION:
        try:
            message = WS_CONNECTION.recv()
        except Exception as e:
            disconnect()  # The disconnect function will also set WS_LISTENER_THREAD to None
            log.error(f"WebSocket connection interrupted: {e}")
            break

        # Process the message
        if isinstance(message, str) and message != "":
            message = json.loads(message)
            log.debug(f"Received websocket message: {message}")
            data = message["data"]

            # Check if the message type is status
            if message["type"] == "status":
                addon_prefs.queue = data["status"]["exec_info"]["queue_remaining"]

                # Force redraw of the UI
                for screen in bpy.data.screens:
                    for area in screen.areas:
                        if area.type in ("VIEW_3D", "IMAGE_EDITOR"):
                            area.tag_redraw()

            # Filter on prompts that are specific to the client
            elif "prompt_id" in data.keys():
                if data["prompt_id"] in prompts_collection.keys():

                    # Reset progress bar to 0 when execution starts
                    if message["type"] == "execution_start":
                        prompts_collection[data["prompt_id"]].status = message["type"]
                        workflow = ast.literal_eval(prompts_collection[data["prompt_id"]].workflow)
                        prompts_collection[data["prompt_id"]].total_nb_nodes = len(workflow)
                        addon_prefs.progress_value = 0.0

                    # Update cached nodes
                    elif message["type"] == "execution_cached":
                        prompts_collection[data["prompt_id"]].status = message["type"]
                        prompts_collection[data["prompt_id"]].nb_nodes_cached = len(data["nodes"])

                    # Check if execution is complete
                    elif message["type"] == "executing":
                        prompts_collection[data["prompt_id"]].status = message["type"]
                        if data["node"] is None:
                            break

                    # Check if the message type is executed with outputs
                    elif message["type"] == "executed":
                        prompts_collection[data["prompt_id"]].status = message["type"]

                        # Get outputs from the workflow
                        key = data["node"]
                        outputs = ast.literal_eval(prompts_collection[data["prompt_id"]].outputs)

                        # Check class type to retrieve 3D outputs
                        if key in outputs and outputs[key]["class_type"] == "BlenderOutputDownload3D":
                            for output in data["output"]["3d"]:
                                filename, filepath = download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                                # Schedule adding 3D model to outputs collection on main thread
                                def add_3d_output(output=output, filename=filename):
                                    model = outputs_collection.add()
                                    model.name = filename
                                    model.filepath = os.path.join(output["subfolder"], filename)
                                    model.type = "3d"
                                    return None

                                # Call function to add output to collection
                                bpy.app.timers.register(add_3d_output, first_interval=0.0)
                            
                            # Force redraw of the UI
                            for screen in bpy.data.screens:
                                for area in screen.areas:
                                    if area.type in ("VIEW_3D", "IMAGE_EDITOR"):
                                        area.tag_redraw()

                        # Check class type to retrieve 3D outputs
                        elif key in outputs and outputs[key]["class_type"] == "BlenderOutputSaveGlb":
                            for output in data["output"]["3d"]:
                                filename, filepath = download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                                # Schedule adding 3D model to outputs collection on main thread
                                def add_3d_output(output=output, filename=filename):
                                    model = outputs_collection.add()
                                    model.name = filename
                                    model.filepath = os.path.join(output["subfolder"], filename)
                                    model.type = "3d"
                                    return None

                                # Call function to add output to collection
                                bpy.app.timers.register(add_3d_output, first_interval=0.0)

                            # Force redraw of the UI
                            for screen in bpy.data.screens:
                                for area in screen.areas:
                                    if area.type in ("VIEW_3D", "IMAGE_EDITOR"):
                                        area.tag_redraw()

                        # Check class type to retrieve image outputs
                        elif key in outputs and outputs[key]["class_type"] == "BlenderOutputSaveImage":
                            for output in data["output"]["images"]:
                                # Check if this is a fixed filename
                                # Fixed filenames: don't match the pattern prefix_NNNNN_.png
                                # Incrementing filenames from SaveImage: match prefix_NNNNN_.png (digits followed by underscore)
                                filename_no_ext = os.path.splitext(output["filename"])[0]

                                # Check if filename ends with pattern like "00001_" (digits followed by underscore)
                                is_incrementing = bool(re.search(r'_\d+_$', filename_no_ext))
                                is_fixed_filename = not is_incrementing

                                log.info(f"Processing output: {output['filename']}, is_fixed={is_fixed_filename}, is_incrementing={is_incrementing}")

                                if is_fixed_filename:
                                    # For fixed filenames, download and overwrite existing file
                                    outputs_folder = get_outputs_folder()
                                    subfolder_path = os.path.join(outputs_folder, output["subfolder"]) if output["subfolder"] else outputs_folder
                                    os.makedirs(subfolder_path, exist_ok=True)
                                    filepath = os.path.join(subfolder_path, output["filename"])

                                    # Download the file (overwriting if exists)
                                    params = {"filename": output["filename"], "subfolder": output["subfolder"], "type": output.get("type", "output"), "rand": os.urandom(8).hex()}
                                    url = get_server_url("/view", params=params)
                                    headers = add_custom_headers({"Content-Type": "application/json"})

                                    try:
                                        response = requests.get(url, params=params, headers=headers, stream=True)
                                        if response.status_code == 200:
                                            with open(filepath, "wb") as file:
                                                for chunk in response.iter_content(chunk_size=8192):
                                                    file.write(chunk)
                                            log.info(f"Fixed filename downloaded and overwritten: {filepath}")
                                        else:
                                            log.error(f"Failed to download fixed filename: {response.status_code}")
                                            continue
                                    except Exception as e:
                                        log.error(f"Error downloading fixed filename: {e}")
                                        continue

                                    filename = output["filename"]
                                else:
                                    # For incrementing filenames, use normal download (which auto-increments)
                                    filename, filepath = download_file(output["filename"], output["subfolder"], output.get("type", "output"))

                                # Schedule adding output to collection on main thread
                                def add_image_output(output=output, filename=filename, filepath=filepath, is_fixed=is_fixed_filename):
                                    log.info(f"add_image_output running: filename={filename}, is_fixed={is_fixed}, filepath={filepath}")

                                    # Check if image already exists in Blender (for fixed filenames)
                                    image_object = None
                                    if is_fixed:
                                        # For fixed filenames, reload existing image if it exists
                                        # Blender stores images with their filename including extension
                                        log.info(f"Looking for existing image: {filename}")
                                        log.info(f"Available images in bpy.data.images: {list(bpy.data.images.keys())}")

                                        if filename in bpy.data.images:
                                            image_object = bpy.data.images[filename]
                                            log.info(f"Found existing image, calling reload()")
                                            image_object.reload()
                                            log.info(f"Reloaded existing fixed filename image: {filename}")

                                            # Force update of any image editors displaying this image
                                            for screen in bpy.data.screens:
                                                for area in screen.areas:
                                                    if area.type == 'IMAGE_EDITOR':
                                                        for space in area.spaces:
                                                            if space.type == 'IMAGE_EDITOR':
                                                                # If this image viewer is showing the reloaded image, force refresh
                                                                current_image_name = space.image.name if space.image else "None"
                                                                log.info(f"Image editor showing: {current_image_name}, looking for: {filename}")
                                                                if space.image and space.image.name == filename:
                                                                    # Force the viewer to update by reassigning the image
                                                                    temp_img = space.image
                                                                    space.image = None
                                                                    space.image = temp_img
                                                                    area.tag_redraw()
                                                                    log.info(f"Forced image viewer refresh for {filename}")
                                        else:
                                            log.info(f"Image {filename} not found in bpy.data.images, will load fresh")

                                    # If not found or not fixed, load as new
                                    if not image_object:
                                        log.info(f"Loading image from {filepath}")
                                        image_object = bpy.data.images.load(filepath, check_existing=True)
                                        image_object.preview_ensure()
                                        log.info(f"Loaded image: {image_object.name}")

                                    # Add image to outputs collection only if not already there
                                    existing_output = None
                                    for existing in outputs_collection:
                                        if existing.name == image_object.name and existing.type == "image":
                                            existing_output = existing
                                            break

                                    if not existing_output:
                                        image = outputs_collection.add()
                                        image.name = image_object.name
                                        image.filepath = os.path.join(output["subfolder"], filename)
                                        image.type = "image"
                                        log.info(f"Added {image_object.name} to outputs collection")
                                    else:
                                        log.info(f"{image_object.name} already in outputs collection")

                                    # Force refresh of image editor to update image list
                                    for screen in bpy.data.screens:
                                        for area in screen.areas:
                                            if area.type == 'IMAGE_EDITOR':
                                                # Tag for redraw
                                                area.tag_redraw()
                                                # Update space data to refresh image list
                                                for space in area.spaces:
                                                    if space.type == 'IMAGE_EDITOR':
                                                        # Trigger update by touching the image property
                                                        if space.image:
                                                            space.image = space.image
                                    return None

                                # Call function to add output to collection
                                bpy.app.timers.register(add_image_output, first_interval=0.0)

                            # Force redraw of the UI
                            for screen in bpy.data.screens:
                                for area in screen.areas:
                                    if area.type in ("VIEW_3D", "IMAGE_EDITOR"):
                                        area.tag_redraw()
                    
                        # Check class type to retrieve text outputs
                        elif key in outputs and outputs[key]["class_type"] == "BlenderOutputString":
                            metadata = outputs[key].get("_meta", {})
                            filename = metadata.get("title", "string") + ".txt"
                            outputs_folder = get_outputs_folder()
                            for output in data["output"]["text"]:
                                filename, filepath = get_filepath(filename, outputs_folder)
                                with open(filepath, "w") as file:
                                    file.write(output)

                                # Schedule adding output to collection on main thread
                                def add_text_output(filename=filename, filepath=filepath):
                                    # Load text into Blender file to get the name
                                    text_object = bpy.data.texts.load(filepath)

                                    # Add text to outputs collection
                                    text = outputs_collection.add()
                                    text.name = text_object.name
                                    text.filepath = filename  # Provide filename as relative path since there is no subfolder
                                    text.type = "text"
                                    return None

                                # Call function to add output to collection
                                bpy.app.timers.register(add_text_output, first_interval=0.0)

                            # Force redraw of the UI
                            for screen in bpy.data.screens:
                                for area in screen.areas:
                                    if area.type in ("VIEW_3D", "IMAGE_EDITOR"):
                                        area.tag_redraw()

                    # Raise error message from ComfyUI server
                    elif message["type"] == "execution_error":
                        # Reset progress and remove prompt from the collection when execution fails
                        prompts_collection.remove(prompts_collection.find(data["prompt_id"]))
                        addon_prefs.progress_value = 0.0
                        error_message = data.get("exception_message", "Unknown error")
                        error_message = f"Execution error from ComfyUI server: {error_message}"
                        log.error(f"{error_message}")

                        # Schedule popup to run on main thread
                        # Do not call the function directly since the thread is not the main thread
                        def raise_error():
                            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                            return None  # Stop the timer

                        # Call function to raise error popup
                        bpy.app.timers.register(raise_error, first_interval=0.0)

                    # Reset progress and remove prompt from the collection when execution is interrupted
                    elif message["type"] == "execution_interrupted":
                        prompts_collection.remove(prompts_collection.find(data["prompt_id"]))
                        addon_prefs.progress_value = 0.0

                    # Remove prompt from the collection when execution completes
                    elif message["type"] == "execution_success":
                        prompts_collection.remove(prompts_collection.find(data["prompt_id"]))
                        addon_prefs.progress_value = 1.0

                    # Update progress bar
                    elif message["type"] == "progress_state":
                        # Percentage of progress contribution per node
                        total_nb_nodes = prompts_collection[data["prompt_id"]].get("total_nb_nodes", 0)
                        nb_nodes_cached = prompts_collection[data["prompt_id"]].get("nb_nodes_cached", 0)
                        nb_nodes_to_execute = total_nb_nodes - nb_nodes_cached
                        node_contribution = 100 / nb_nodes_to_execute if nb_nodes_to_execute > 0 else 100

                        # Get progress from executing nodes
                        workflow_progress = 0
                        for key, node in data["nodes"].items():
                            node_progress = node["value"] / node["max"] * node_contribution
                            workflow_progress += node_progress

                        # Update progress value
                        addon_prefs.progress_value = workflow_progress / 100.0

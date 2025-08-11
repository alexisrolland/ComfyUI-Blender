import logging
import os
import random
import requests
import textwrap
from urllib.parse import urljoin

import bpy

log = logging.getLogger("comfyui_blender")


def download_file(filename, subfolder, type="output"):
    """Download a file from the ComfyUI server."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    server_address = addon_prefs.server_address
    outputs_folder = addon_prefs.outputs_folder

    # Download the file data from the ComfyUI server
    # Add a random parameter to avoid caching issues
    params = {"filename": filename, "subfolder": subfolder, "type": type, "rand": random.random()}
    url = f"{server_address}/view"

    # Download with streaming to handle large files and avoid memory issues
    response = requests.get(url, params=params, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Save the file in the output folder
    folder = os.path.join(outputs_folder, subfolder)
    filepath = os.path.join(folder, filename)

    # Create subfolder if it does not exist
    os.makedirs(folder, exist_ok=True)

    with open(filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive chunks
                file.write(chunk)

def get_filepath(filename, folder):
    """Handle file names conflicts when importing files, by appending an incremental number"""

    filepath = os.path.join(folder, filename)    
    if os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(folder, f"{name}_{counter}{ext}")):
            counter += 1
        
        # Rename input file
        filename = f"{name}_{counter}{ext}"
        filepath = os.path.join(folder, filename)
    return filename, filepath

def show_error_popup(message):
    """Show an error popup."""

    def draw(self, context):
        self.layout

        # Wrap text to specified width
        wrapped_lines = textwrap.wrap(message, width=70)
        for line in wrapped_lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title="Execution Error", icon="ERROR")

def upload_file(filepath, type, subfolder=None, overwrite=False):
    """Upload a file to the ComfyUI server."""

    # Get server address
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences

    # Prepare form data
    data = {}
    if overwrite:
        data["overwrite"] = True

    # Read file data
    with open(filepath, "rb") as file:
        file_data = file.read()

    # Extract filename from the filepath
    filename = os.path.basename(filepath)

    # Build request according to the file type
    if type == "3d":
        data["subfolder"] = "3d"
        if subfolder:
            data["subfolder"] = os.path.join(data["subfolder"], subfolder)

    elif type == "image":
        if subfolder:
            data["subfolder"] = subfolder

    files = {"image": (filename, file_data)}
    url = urljoin(addon_prefs.server_address, "/upload/image")
    response = requests.post(url, files=files, data=data)
    return response

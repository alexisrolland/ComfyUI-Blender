import bpy
import os
import requests
import urllib.request
import urllib.parse


def download_file(filename, subfolder):
    """Download a file from the ComfyUI server."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    server_address = addon_prefs.server_address
    outputs_folder = addon_prefs.outputs_folder

    # Download the file data from the ComfyUI server
    data = {"filename": filename, "subfolder": subfolder, "type": "output"}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{server_address}/view?{url_values}") as response:
        file_data = response.read()

    # Save the file in the output folder
    folder = os.path.join(outputs_folder, subfolder)
    filepath = os.path.join(folder, filename)

    # Create subfolder if it does not exist
    os.makedirs(folder, exist_ok=True)
    with open(filepath, "wb") as file:
        file.write(file_data)

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

def upload_file(filepath, type, subfolder=None, overwrite=False):
    """Upload a file to the ComfyUI server."""

    # Get server address
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences

    # Prepare form data
    data = {}
    if overwrite:
        data["overwrite"] = True
    if subfolder:
        data["subfolder"] = subfolder

    # Read file data
    with open(filepath, "rb") as file:
        file_data = file.read()

    # Extract filename from the filepath
    filename = os.path.basename(filepath)

    # Build request according to the file type
    if type == "image":
        files = {"image": (filename, file_data)}
        url = addon_prefs.server_address + "/upload/image"

    response = requests.post(url, files=files, data=data)
    return response

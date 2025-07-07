import bpy
import os
import urllib.request
import urllib.parse


def download_image(filename, subfolder, type):
    """Download an image from the ComfyUI server."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    server_address = addon_prefs.server_address
    outputs_folder = addon_prefs.outputs_folder

    # Download the image data from the ComfyUI server
    data = {"filename": filename, "subfolder": subfolder, "type": type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{server_address}/view?{url_values}") as response:
        image_data = response.read()

    # Save the image in the output folder
    folder = os.path.join(outputs_folder, subfolder)
    filepath = os.path.join(folder, filename)

     # Create subfolder if it does not exist
    os.makedirs(folder, exist_ok=True)
    with open(filepath, 'wb') as file:
        file.write(image_data)


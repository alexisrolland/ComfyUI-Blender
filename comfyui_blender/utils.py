import bpy
import os
import urllib.request
import urllib.parse
from bpy.props import (
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty
)

def create_dynamic_properties(workflow_name, inputs):
    """Create dynamic properties for each input of the workflow."""

    for key, node in inputs.items():
        metadata = node.get("_meta", {})
        name = metadata.get("title", f"Node {key}")

        # Combo box
        if node["class_type"] == "BlenderInputCombo":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", EnumProperty(
                name=name,
                default=node["inputs"].get("default", ""),
                items=[(i, i, "") for i in node["inputs"]["list"].split("\n")]
            ))

        # Float
        if node["class_type"] == "BlenderInputFloat":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", FloatProperty(
                name=name,
                default=node["inputs"].get("default", 0.0),
                min=node["inputs"].get("min", -1e38),
                max=node["inputs"].get("max", 1e38),
                step=node["inputs"].get("step", 0.01)
            ))

        # Integer
        if node["class_type"] == "BlenderInputInt":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", -2147483648),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            ))
        
        # String
        if node["class_type"] == "BlenderInputString":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            ))

        # String Multiline
        elif node["class_type"] == "BlenderInputStringMultiline":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            ))

def download_image(filename, subfolder, type):
    """Download an image from the ComfyUI server."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    server_address = addon_prefs.server_address
    output_folder = addon_prefs.output_folder

    # Download the image data from the ComfyUI server
    data = {"filename": filename, "subfolder": subfolder, "type": type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{server_address}/view?{url_values}") as response:
        image_data = response.read()

    # Save the image in the output folder
    filepath = os.path.join(output_folder, subfolder, filename)
    with open(filepath, 'wb') as file:
        file.write(image_data)

def get_workflow_list(self, context):
    """Return a list of workflows JSON files from the workflows folder."""

    addon_prefs = context.preferences.addons["comfyui_blender"].preferences
    workflow_folder = addon_prefs.workflow_folder
    workflows = []

    if os.path.exists(workflow_folder) and os.path.isdir(workflow_folder):
        for file in sorted(os.listdir(workflow_folder)):
            if file.endswith(".json"):
                workflows.append((file, file, ""))

    # Default to empty tuple if there are no workflow
    if not workflows:
        workflows = [("none", "None", "No workflow available")]
    return workflows

def parse_workflow_for_inputs(workflow):
    """Parse a workflow dictionary and extract nodes with 'class_type' starting with 'BlenderInput...'."""

    inputs = {}
    for key, node in workflow.items():
        if node.get("class_type").startswith("BlenderInput"):
            inputs[key]=node

    if len(inputs) > 0:
        # Reorder the keys based on the "order" property of the nodes dictionaries
        sorted_keys = sorted(inputs.keys(), key=lambda k: inputs[k]["inputs"]["order"])

        # Create a new dictionary with the sorted keys
        sorted_inputs = {key: inputs[key] for key in sorted_keys}
    return sorted_inputs

def parse_workflow_for_outputs(workflow):
    """Parse a workflow dictionary and extract nodes with 'class_type' starting with 'BlenderOutput...'."""

    outputs = {}
    for key, node in workflow.items():
        if node.get("class_type").startswith("BlenderOutput"):
            outputs[key]=node
    return outputs

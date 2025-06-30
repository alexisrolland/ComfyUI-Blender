import bpy
import os
import json

def get_workflow_list(self, context):
    """Return a list of workflows JSON files from the workflows folder."""
    addon_prefs = context.preferences.addons["comfyui_blender_plugin"].preferences
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

def parse_workflow_for_inputs(workflow_path):
    """Parse the workflow JSON file and extract nodes with 'class_type' starting with 'BlenderInput...'."""
    inputs = {}
    try:
        with open(workflow_path, "r") as f:
            workflow_data = json.load(f)
            for key, node in workflow_data.items():
                if node.get("class_type").startswith("BlenderInput"):
                    inputs[key]=node
    except Exception as e:
        print(f"Failed to parse workflow: {e}")

    if len(inputs) > 0:
        # Reorder the keys based on the "order" property of the nodes dictionaries
        sorted_keys = sorted(inputs.keys(), key=lambda k: inputs[k]["inputs"]["order"])

        # Create a new dictionary with the sorted keys
        sorted_inputs = {key: inputs[key] for key in sorted_keys}
    return sorted_inputs

def create_dynamic_properties(workflow_name, inputs):
    """Create dynamic properties for each input of the workflow."""
    for key, node in inputs.items():
        metadata = node.get("_meta", {})
        name = metadata.get("title", f"Node {key}")

        if node["class_type"] == "BlenderInputCombo":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.EnumProperty(
                name=name,
                default=node["inputs"].get("default", ""),
                items=[(i, i, "") for i in node["inputs"]["list"].split("\n")]
            ))

        if node["class_type"] == "BlenderInputFloat":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.FloatProperty(
                name=name,
                default=node["inputs"].get("default", 0.0),
                min=node["inputs"].get("min", -1e38),
                max=node["inputs"].get("max", 1e38),
                step=node["inputs"].get("step", 0.01)
            ))

        if node["class_type"] == "BlenderInputInt":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", -2147483648),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            ))
        
        if node["class_type"] == "BlenderInputString":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            ))

        elif node["class_type"] == "BlenderInputStringMultiline":
            setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            ))

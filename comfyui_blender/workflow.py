"""Functions to create dynamic workflow classes and properties"""
import hashlib
import json
import logging
import os
import re
import struct

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    IntVectorProperty,
    StringProperty
)

log = logging.getLogger("comfyui_blender")


def check_workflow_file_exists(new_workflow_data, workflows_folder):
    """Check if a workflow already exists and return the name of the existing file."""

    # Create normalized content and hash for new workflow
    new_content = json.dumps(new_workflow_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    new_hash = hashlib.sha256(new_content).hexdigest()

    # Loop over existing files
    for filename in os.listdir(workflows_folder):
        if filename.endswith(".json"):
            # Load existing workflow data
            filepath = os.path.join(workflows_folder, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                existing_workflow_data = json.load(file)

            # Create normalized content and hash for existing workflow
            existing_content = json.dumps(existing_workflow_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
            existing_hash = hashlib.sha256(existing_content).hexdigest()
 
            # Compare hashes
            if new_hash == existing_hash:
                return filename

def create_class_properties(inputs, keep_values=False):
    """Create properties for each input and output of the workflow."""

    # Create a dictionary to extract input groups
    # Expected format: {group_key: [node_keys]}
    input_groups = {}
    for key, node in inputs.items():
        if node["class_type"].startswith("BlenderInput"):
            if "group" not in node["inputs"]:
                continue
            group_key = node["inputs"]["group"][0]
            if group_key not in input_groups:
                input_groups[group_key] = []
            input_groups[group_key].append(key)

    # Sort node keys in each input group
    for group_key in input_groups:
        input_groups[group_key].sort(key=lambda k: inputs[k]["inputs"]["order"])

    # Create properties
    properties = {}
    for key, node in inputs.items():
        property_name = f"node_{key}"
        metadata = node.get("_meta", {})
        name = metadata.get("title", f"Node {key}")

        # Input properties
        # Boolean
        if node["class_type"] == "BlenderInputBoolean":
            properties[property_name] = BoolProperty(
                name=name,
                default=node["inputs"].get("default", False)
            )
            continue

        # Combo box
        if node["class_type"] == "BlenderInputCombo":
            # If default value not in list, set to first item in the list
            default = node["inputs"].get("default", "")
            items = node["inputs"]["list"].split("\n")
            if default not in items:
                default = items[0]

            properties[property_name] = EnumProperty(
                name=name,
                default=default,
                items=[(i, i, "") for i in items]
            )
            continue

        # Float
        if node["class_type"] == "BlenderInputFloat":
            properties[property_name] = FloatProperty(
                name=name,
                default=node["inputs"].get("default", 0.0),
                min=node["inputs"].get("min", -1e38),
                max=node["inputs"].get("max", 1e38),
                # Step size is weird, value of 1 gives a step of 0.1, so I'm deactivating it for now
                # step=node["inputs"].get("step", 1.0),
                step=1,
                precision=2
            )
            continue

        # Group
        if node["class_type"] == "BlenderInputGroup":
            properties[property_name] = IntVectorProperty(
                name=name,
                size=len(input_groups[key]),
                default=tuple(int(node_key) for node_key in input_groups[key])
            )
            continue

        # Integer
        if node["class_type"] == "BlenderInputInt":
            properties[property_name] = IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", -2147483648),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            )
            continue

        # Load 3D and Load image
        if node["class_type"] in ("BlenderInputLoad3D", "BlenderInputLoadImage"):
            properties[property_name] = StringProperty(name=name)
            continue
        
        # Seed
        if node["class_type"] == "BlenderInputSeed":
            properties[property_name] = IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", 0),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            )
            continue

        # String and String multiline
        if node["class_type"] in ("BlenderInputString", "BlenderInputStringMultiline"):
            properties[property_name] = StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            )
            continue
    return properties

def create_workflow_class(class_name, properties):
    """Create a new PropertyGroup class for a workflow."""

    # Create the new class
    new_class = type(class_name, (bpy.types.PropertyGroup,), {})

    # Add properties to the class
    for prop_name, prop_details in properties.items():
        setattr(new_class, prop_name, prop_details)

    # Manually add the annotations attribute
    new_class.__annotations__ = {prop_name: properties[prop_name] for prop_name in properties}
    return new_class

def extract_workflow_from_metadata(filepath):
    """Extract workflow from the metadata of a file."""
    
    def _read_glb_metadata(filepath):
        """Read .glb file metadata to extract JSON chunk"""

        with open(filepath, "rb") as file:
            header = file.read(12)
            magic, version, length = struct.unpack("<4sII", header)
            offset = 12
            while offset < length:
                chunk_header = file.read(8)
                if len(chunk_header) < 8:
                    break
                chunk_len, chunk_type = struct.unpack("<I4s", chunk_header)
                chunk_data = file.read(chunk_len)
                if chunk_type == b"JSON":
                    return json.loads(chunk_data.decode("utf-8"))
                offset += 8 + chunk_len
        return None

    def _read_png_metadata(filepath):
        """Read .png file metadata to extract JSON chunk"""

        def _chunk_iter(data):
            """Iterate over PNG data chunks to extract metadata. This function was borrowed from:
            https://blender.stackexchange.com/questions/35504/read-image-metadata-from-python"""

            total_length = len(data)
            end = 4

            while(end + 8 < total_length):     
                length = int.from_bytes(data[end + 4: end + 8], 'big')
                begin_chunk_type = end + 8
                begin_chunk_data = begin_chunk_type + 4
                end = begin_chunk_data + length
                yield (data[begin_chunk_type: begin_chunk_data], data[begin_chunk_data: end])

        with open(filepath, "rb") as file:
            data = file.read()
            for chunk_type, chunk_data in _chunk_iter(data):
                if chunk_type == b'tEXt':
                    key, value = chunk_data.decode("iso-8859-1").split("\0")
                    try:
                        return {key: json.loads(value)}
                    except Exception as e:
                        return None

    # GLB metadata extraction
    if filepath.lower().endswith(".glb"):
        metadata = _read_glb_metadata(filepath)

        # Add a flag to keep current values when reloading the workflow
        # Instead of using the default values
        if metadata.get("asset"):
            metadata["prompt"] = json.loads(metadata["asset"]["extras"]["prompt"])
            metadata["prompt"]["comfyui_blender"] = {}
            metadata["prompt"]["comfyui_blender"]["keep_values"] = True
            return metadata["prompt"]
        else:
            return None

    # OBJ metadata extraction
    if filepath.lower().endswith(".obj"):
        # Placeholder for future implementation
        # Reloading workflow from .obj files depends whether file is saved with metadata on ComfyUI server side
        return None

    # PNG metadata extraction
    elif filepath.lower().endswith(".png"):
        metadata = _read_png_metadata(filepath)

        # Add a flag to keep current values when reloading the workflow
        # Instead of using the default values
        if metadata.get("prompt"):
            metadata["prompt"]["comfyui_blender"] = {}
            metadata["prompt"]["comfyui_blender"]["keep_values"] = True
            return metadata["prompt"]
        else:
            return None

    # File type is not supported
    else:
        return None

def get_workflow_class_name(workflow_filename):
    """Generate a class name from the workflow file name."""

    workflow_name = os.path.splitext(workflow_filename)[0]
    class_name = f"wkf_{workflow_name}"
    class_name = re.sub(r"[^a-zA-Z0-9_]", "_", class_name).lower()
    return class_name

def get_workflow_list(self, context):
    """Return a list of workflow JSON files from the workflows folder."""

    addon_prefs = context.preferences.addons["comfyui_blender"].preferences
    workflows_folder = addon_prefs.workflows_folder
    workflows = []

    if os.path.exists(workflows_folder) and os.path.isdir(workflows_folder):
        for file in sorted(os.listdir(workflows_folder)):
            if file.endswith(".json"):
                filepath = os.path.join(workflows_folder, file)
                workflows.append((file, file, filepath))

    # Default to empty tuple if there are no workflow
    if not workflows:
        workflows = [("none", "None", "No workflow available")]
    return workflows

def parse_workflow_for_inputs(workflow):
    """Parse a workflow dictionary and extract nodes with 'class_type' starting with 'BlenderInput...'."""

    inputs = {}
    sorted_inputs = inputs
    for key, node in workflow.items():
        class_type = node.get("class_type")
        if class_type:
            if class_type.startswith("BlenderInput"):
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
        class_type = node.get("class_type")
        if class_type:
            if class_type.startswith("BlenderOutput"):
                outputs[key]=node
    return outputs

def register_workflow_class(self, context):
    """Wrapper function to register a workflow class."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    workflows_folder = str(addon_prefs.workflows_folder)
    workflow_filename = str(self.workflow)
    workflow_path = os.path.join(workflows_folder, workflow_filename)
    workflow_class_name = get_workflow_class_name(workflow_filename)

    # Unregister workflow class if it already exists
    for subclass in bpy.types.PropertyGroup.__subclasses__():
        if subclass.__name__==workflow_class_name and subclass.is_registered:
            bpy.utils.unregister_class(subclass)

    # Load the workflow JSON file
    if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
        with open(workflow_path, "r",  encoding="utf-8") as file:
            workflow = json.load(file)

        # Get inputs from the workflow
        inputs = parse_workflow_for_inputs(workflow)
        properties = create_class_properties(inputs)
        workflow_class = create_workflow_class(workflow_class_name, properties)

        # Register the workflow class
        bpy.utils.register_class(workflow_class)
        bpy.types.Scene.current_workflow = bpy.props.PointerProperty(type=workflow_class)

        # Get custom data from the workflow
        keep_values = False
        if workflow.get("comfyui_blender"):
            keep_values = workflow["comfyui_blender"].get("keep_values", False)

        # Overwrite values after registration
        # Note keep_values is set to True when reloading a workflow from outputs
        if hasattr(context.scene, "current_workflow") and keep_values:
            workflow_instance = context.scene.current_workflow
            for key, node in inputs.items():
                property_name = f"node_{key}"

                if hasattr(workflow_instance, property_name):
                    # Custom handling for 3D model input
                    if node["class_type"] == "BlenderInputLoad3D":
                        setattr(workflow_instance, property_name, node["inputs"].get("model_file", ""))
                    
                    # Custom handling for image input
                    elif node["class_type"] == "BlenderInputLoadImage":
                        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
                        inputs_folder = str(addon_prefs.inputs_folder)
                        input_filename = node["inputs"].get("image", "")
                        input_filepath = os.path.join(inputs_folder, input_filename)

                        # Load image in the data block and update the workflow property
                        if os.path.exists(input_filepath):
                            image = bpy.data.images.load(input_filepath, check_existing=True)
                            setattr(workflow_instance, property_name, image.name)

                    else:
                        # Default handling for other input types
                        setattr(workflow_instance, property_name, node["inputs"].get("value", ""))

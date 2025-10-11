"""Functions to create dynamic workflow classes and properties"""
import hashlib
import json
import logging
import os
import re
import shutil
import struct

import bpy
import requests
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    IntVectorProperty,
    PointerProperty,
    StringProperty
)

from .utils import (
    add_custom_headers,
    contains_non_latin,
    get_server_url,
    upload_file
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


def create_class_properties(inputs):
    """Create properties for each input and output of the workflow."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences

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

        # Combo box
        elif node["class_type"] == "BlenderInputCombo":
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

        # Float
        elif node["class_type"] == "BlenderInputFloat":
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

        # Group, if the group is empty (not connected to any other node), create a dummy property
        elif node["class_type"] == "BlenderInputGroup":
            if input_groups:
                properties[property_name] = IntVectorProperty(
                    name=name,
                    size=len(input_groups[key]),
                    default=tuple(int(node_key) for node_key in input_groups[key])
                )
            else:
                properties[property_name] = IntVectorProperty(name=name, size=1, default=(-1,))

        # Integer
        elif node["class_type"] == "BlenderInputInt":
            properties[property_name] = IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", -2147483648),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            )

        # Load 3D
        elif node["class_type"] == "BlenderInputLoad3D":
            properties[property_name] = StringProperty(name=name)

        # Load checkpoint
        elif node["class_type"] == "BlenderInputLoadCheckpoint":
            if addon_prefs.connection_status:
                # Get list of checkpoints from the ComfyUI server
                url = get_server_url("/models/checkpoints")
                headers = {"Content-Type": "application/json"}
                headers = add_custom_headers(headers)
                try:
                    response = requests.get(url, headers=headers, stream=True)
                except Exception as e:
                    error_message = f"Failed to get list of checkpoints from ComfyUI server: {url}. {e}"
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.exception(error_message)
                    # This crashes Blender upon starting if the ComfyUI server is not reachable
                    # bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue

                if response.status_code != 200:
                    error_message = error_message = f"Failed to get list of checkpoints from ComfyUI server: {url}."
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.error(error_message)
                    # This crashes Blender upon starting if the ComfyUI server is not reachable
                    # bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue

                items = response.json()
                if not items:
                    error_message = error_message = f"There is no checkpoint on the ComfyUI server: {url}."
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.error(error_message)
                    continue

                # If default value not in list, set to first item in the list
                default = node["inputs"].get("default", "")
                if default not in items:
                    default = items[0]

                properties[property_name] = EnumProperty(
                    name=name,
                    default=default,
                    items=[(i, i, "") for i in items]
                )
            else:
                message = "Add-on not connect to the ComfyUI server."
                properties[property_name] = StringProperty(name=name, default=message)

        # Load diffusion model
        elif node["class_type"] == "BlenderInputLoadDiffusionModel":
            if addon_prefs.connection_status:
                # Get list of diffusion models from the ComfyUI server
                url = get_server_url("/models/diffusion_models")
                headers = {"Content-Type": "application/json"}
                headers = add_custom_headers(headers)
                try:
                    response = requests.get(url, headers=headers, stream=True)
                except Exception as e:
                    error_message = f"Failed to get list of diffusion models from ComfyUI server: {url}. {e}"
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.exception(error_message)
                    # This crashes Blender upon starting if the ComfyUI server is not reachable
                    # bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue

                if response.status_code != 200:
                    error_message = error_message = f"Failed to get list of diffusion models from ComfyUI server: {url}."
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.error(error_message)
                    # This crashes Blender upon starting if the ComfyUI server is not reachable
                    # bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue

                items = response.json()
                if not items:
                    error_message = error_message = f"There is no diffusion model on the ComfyUI server: {url}."
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.error(error_message)
                    continue

                # If default value not in list, set to first item in the list
                default = node["inputs"].get("default", "")
                if default not in items:
                    default = items[0]

                properties[property_name] = EnumProperty(
                    name=name,
                    default=default,
                    items=[(i, i, "") for i in items]
                )
            else:
                message = "Add-on not connect to the ComfyUI server."
                properties[property_name] = StringProperty(name=name, default=message)

        # Load image and load mask
        # Use a lambda function to pass arguments to upload_input
        elif node["class_type"] in ("BlenderInputLoadImage", "BlenderInputLoadMask"):
            properties[property_name] = PointerProperty(
                name=name,
                type=bpy.types.Image,
                update=upload_input_callback(property_name)
            )

        # Load LoRA
        elif node["class_type"] == "BlenderInputLoadLora":
            if addon_prefs.connection_status:
                # Get list of loras from the ComfyUI server
                url = get_server_url("/models/loras")
                headers = {"Content-Type": "application/json"}
                headers = add_custom_headers(headers)
                try:
                    response = requests.get(url, headers=headers, stream=True)
                except Exception as e:
                    error_message = f"Failed to get list of LoRAs from ComfyUI server: {url}. {e}"
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.exception(error_message)
                    # This crashes Blender upon starting if the ComfyUI server is not reachable
                    # bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue

                if response.status_code != 200:
                    error_message = error_message = f"Failed to get list of LoRAs from ComfyUI server: {url}."
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.error(error_message)
                    # This crashes Blender upon starting if the ComfyUI server is not reachable
                    # bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue

                items = response.json()
                if not items:
                    error_message = error_message = f"There is no LoRA on the ComfyUI server: {url}."
                    properties[property_name] = StringProperty(name=name, default=error_message)  # Create dummy property with error message
                    log.error(error_message)
                    continue

                # If default value not in list, set to first item in the list
                default = node["inputs"].get("default", "")
                if default not in items:
                    default = items[0]

                properties[property_name] = EnumProperty(
                    name=name,
                    default=default,
                    items=[(i, i, "") for i in items]
                )
            else:
                message = "Add-on not connect to the ComfyUI server."
                properties[property_name] = StringProperty(name=name, default=message)

        # Sampler
        elif node["class_type"] == "BlenderInputSampler":
            # We should fetch the list dynamically from the ComfyUI server, pending on PR: https://github.com/comfyanonymous/ComfyUI/pull/10197
            items = ["ddim", "ddpm", "deis", "dpm_2", "dpm_2_ancestral", "dpm_adaptive", "dpm_fast", "dpmpp_2m", "dpmpp_2m_cfg_pp", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_2m_sde_heun", "dpmpp_2m_sde_heun_gpu", "dpmpp_2s_ancestral", "dpmpp_2s_ancestral_cfg_pp", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "dpmpp_sde", "dpmpp_sde_gpu", "er_sde", "euler", "euler_ancestral", "euler_ancestral_cfg_pp", "euler_cfg_pp", "gradient_estimation", "gradient_estimation_cfg_pp", "heun", "heunpp2", "ipndm", "ipndm_v", "lcm", "lms", "res_multistep", "res_multistep_ancestral", "res_multistep_ancestral_cfg_pp", "res_multistep_cfg_pp", "sa_solver", "sa_solver_pece", "seeds_2", "seeds_3", "uni_pc", "uni_pc_bh2"]

            # If default value not in list, set to first item in the list
            default = node["inputs"].get("default", "")
            if default not in items:
                default = items[0]

            properties[property_name] = EnumProperty(
                name=name,
                default=default,
                items=[(i, i, "") for i in items]
            )

        # Seed
        elif node["class_type"] == "BlenderInputSeed":
            properties[property_name] = IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", 0),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            )

        # String and String multiline
        elif node["class_type"] == "BlenderInputString":
            properties[property_name] = StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            )

        # String multiline
        elif node["class_type"] == "BlenderInputStringMultiline":
            properties[property_name] = PointerProperty(name=name, type=bpy.types.Text)
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
        if metadata:
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
        if metadata:
            if metadata.get("prompt"):
                metadata["prompt"]["comfyui_blender"] = {}
                metadata["prompt"]["comfyui_blender"]["keep_values"] = True
                return metadata["prompt"]
            else:
                return None

    # File type is not supported
    else:
        return None


def get_current_workflow_inputs(self, context, input_types):
    """Function to get the list of inputs from the current workflow based on their type."""

    # List of inputs to send the image to
    target_inputs = []
    addon_prefs = context.preferences.addons["comfyui_blender"].preferences
    if hasattr(context.scene, "current_workflow"):
        # Get the selected workflow
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_filename)

        # Load the workflow JSON file
        if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
            with open(workflow_path, "r",  encoding="utf-8") as file:
                workflow = json.load(file)

            # Get sorted inputs from the workflow
            inputs = parse_workflow_for_inputs(workflow)

            # Get workflow inputs of type load image or load mask
            for key, node in inputs.items():
                if node["class_type"] in input_types:
                    property_name = f"node_{key}"
                    metadata = node.get("_meta", {})
                    name = metadata.get("title", f"Node {key}")
                    target_inputs.append((property_name, name, ""))
    return target_inputs


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
            if file.endswith(".json") and not contains_non_latin(file):
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


def upload_input_callback(property_name):
    """
    Create a unique upload callback function when for the workflow property.
    We need to do this because the workflow properties are created dynamically in a loop.
    """

    def upload_input(self, context):
        """Upload an input image or mask to the ComfyUI server."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        image = getattr(self, property_name)
        previous_filepath = image.filepath

        # Upload file on ComfyUI server
        try:
            response = upload_file(previous_filepath, type="image")
        except Exception as e:
            error_message = f"Failed to upload file to ComfyUI server: {addon_prefs.server_address}. {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)

        if response.status_code != 200:
            # Reset the scene to initial state
            error_message = f"Failed to upload file: {response.status_code} - {response.text}"
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)

        # Build input file paths
        inputs_folder = str(addon_prefs.inputs_folder)
        input_subfolder = response.json()["subfolder"]
        input_filename = response.json()["name"]
        input_filepath = os.path.join(inputs_folder, input_subfolder, input_filename)

        # Create the input subfolder if it doesn't exist
        os.makedirs(os.path.join(inputs_folder, input_subfolder), exist_ok=True)

        try:
            # Copy the file to the inputs folder
            shutil.copy(previous_filepath, input_filepath)
            log.info(f"Input file copied to: {input_filepath}")
        except shutil.SameFileError as e:
            log.info(f"Input file is already in the inputs folder: {input_filepath}")
        except Exception as e:
            error_message = f"Failed to copy input file: {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)

        # Load image in the data block
        # image = bpy.data.images.load(input_filepath, check_existing=True)

        # Update image name and path in the data block
        image.name = input_filename
        image.filepath = input_filepath
        image.reload()

    return upload_input
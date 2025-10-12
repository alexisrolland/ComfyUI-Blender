"""Operator to send and execute a workflow on ComfyUI server."""
import json
import logging
import os
import random
import requests

import bpy

from .. import workflow as w
from ..utils import add_custom_headers, get_server_url

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorRunWorkflow(bpy.types.Operator):
    """Operator to send and execute a workflow on ComfyUI server."""

    bl_idname = "comfy.run_workflow"
    bl_label = "Run Workflow"
    bl_description = "Send the workflow to the ComfyUI server."

    def execute(self, context):
        """Execute the operator."""

        # Get add-on preferences and selected workflow
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_filename)

        # Verify workflow JSON file exists
        if not os.path.exists(workflow_path):
            error_message = f"Workflow file does not exist: {workflow_path}"
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Load the workflow JSON file
        with open(workflow_path, "r",  encoding="utf-8") as file:
            workflow = json.load(file)

        # Get inputs and outputs from the workflow
        inputs = w.parse_workflow_for_inputs(workflow)
        outputs = w.parse_workflow_for_outputs(workflow)

        # Update workflow content with user inputs
        current_workflow = context.scene.current_workflow
        for key, node in inputs.items():
            property_name = f"node_{key}"

            # Custom handling for group of inputs
            if node["class_type"] == "BlenderInputGroup":
                # Do nothing, groups are just containers
                continue

            # Custom handling for sampler input
            elif node["class_type"] == "BlenderInputSampler":
                workflow[key]["inputs"]["sampler_name"] = getattr(current_workflow, property_name)

            # Custom handling for 3D model input
            elif node["class_type"] == "BlenderInputLoad3D":
                property_value = getattr(current_workflow, property_name)
                if property_value:
                    workflow[key]["inputs"]["model_file"] = property_value
                else:
                    property_name = current_workflow.bl_rna.properties[property_name].name  # Node title
                    error_message = f"Input {property_name} is empty."
                    log.error(error_message)
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}

            # Custom handling for load checkpoint input
            elif node["class_type"] == "BlenderInputLoadCheckpoint":
                workflow[key]["inputs"]["ckpt_name"] = getattr(current_workflow, property_name)

            # Custom handling for load diffusion model input
            elif node["class_type"] == "BlenderInputLoadDiffusionModel":
                workflow[key]["inputs"]["unet_name"] = getattr(current_workflow, property_name)

            # Custom handling for load image input
            elif node["class_type"] in ("BlenderInputLoadImage", "BlenderInputLoadMask"):
                # Get add-on preferences
                addon_prefs = context.preferences.addons["comfyui_blender"].preferences
                inputs_folder = str(addon_prefs.inputs_folder)

                # Get image relative path in the inputs folder
                image = getattr(current_workflow, property_name)
                if not image:
                    property_name = current_workflow.bl_rna.properties[property_name].name  # Node title
                    error_message = f"Input {property_name} is empty."
                    log.error(error_message)
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}

                # Update the workflow with the relative path
                # Get image absolute path in case it was converted to relative path like //..\AppData\Roaming\...
                image_absolute_path = bpy.path.abspath(image.filepath)
                image_path = os.path.relpath(image_absolute_path, inputs_folder)
                if image_path:
                    workflow[key]["inputs"]["image"] = image_path
                else:
                    property_name = current_workflow.bl_rna.properties[property_name].name  # Node title
                    error_message = f"Input {property_name} is empty."
                    log.error(error_message)
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}

            # Custom handling for load LoRA input
            elif node["class_type"] == "BlenderInputLoadLora":
                workflow[key]["inputs"]["lora_name"] = getattr(current_workflow, property_name)

            # Custom handling for seed inputs
            elif node["class_type"] == "BlenderInputSeed":
                seed = getattr(current_workflow, property_name)
                workflow[key]["inputs"]["value"] = seed

                # If lock seed is not enabled, generate a new random seed
                if not addon_prefs.lock_seed:
                    min = current_workflow.bl_rna.properties[property_name].hard_min
                    max = current_workflow.bl_rna.properties[property_name].hard_max
                    seed = random.randint(min, max)
                    setattr(current_workflow, property_name, seed)

            # Custom handling for string multiline inputs
            elif node["class_type"] == "BlenderInputStringMultiline":
                text = getattr(current_workflow, property_name)
                if not text:
                    property_name = current_workflow.bl_rna.properties[property_name].name  # Node title
                    error_message = f"Input {property_name} is empty."
                    log.error(error_message)
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}

                # Update the workflow with the text content
                workflow[key]["inputs"]["value"] = text.as_string()

            else:
                # Default handling for other input types
                workflow[key]["inputs"]["value"] = getattr(current_workflow, property_name)

        # Remove custom data from the workflow to avoid error from ComfyUI server
        workflow.pop("comfyui_blender", None)

        # Send workflow to ComfyUI server
        data = {"prompt": workflow, "client_id": addon_prefs.client_id}
        url = get_server_url("/prompt")
        headers = {"Content-Type": "application/json"}
        headers = add_custom_headers(headers)
        try:
            response = requests.post(url, json=data, headers=headers)
        except Exception as e:
            error_message = f"Failed to send run workflow request to ComfyUI server: {addon_prefs.server_address}. {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        if response.status_code != 200:
            error_message = response.text
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        response_data = response.text
        prompt_id = json.loads(response_data).get("prompt_id", "")
        self.report({'INFO'}, "Workflow sent to ComfyUI server.")

        # Add the prompt to the prompt collection
        prompt = addon_prefs.prompts_collection.add()
        prompt.name = prompt_id
        prompt.workflow = str(workflow)
        prompt.outputs = str(outputs)
        prompt.status = "pending"
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRunWorkflow)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRunWorkflow)

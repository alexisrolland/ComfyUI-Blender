"""Operator to send and execute a workflow on ComfyUI server."""
import json
import logging
import os
import random
import requests
import threading

import bpy

from .. import connection
from .. import workflow as w
from ..utils import add_custom_headers, get_server_url

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorRunWorkflow(bpy.types.Operator):
    """Operator to send and execute a workflow on ComfyUI server."""

    bl_idname = "comfy.run_workflow"
    bl_label = "Run Workflow"
    bl_description = "Send the workflow to the ComfyUI server"

    def execute(self, context):
        """Execute the operator."""

        # Get add-on preferences and selected workflow
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_filename)

        # Try to establish WebSocket connection with ComfyUI server first
        if not connection.WS_CONNECTION:
            self.report({'INFO'}, "Connecting to server...")
            try:
                connection.connect()
                self.report({'INFO'}, "Connection established.")
            except Exception as e:
                error_message = f"Failed to connect to ComfyUI server: {addon_prefs.server_address}. {e}"
                log.exception(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, "Reusing existing connection.")

        # Verify workflow JSON file exists
        if not os.path.exists(workflow_path):
            error_message = f"Workflow file does not exist: {workflow_path}"
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

            # Custom handling for 3D model input
            if node["class_type"] == "BlenderInputLoad3D":
                property_value = getattr(current_workflow, property_name)
                if property_value:
                    workflow[key]["inputs"]["model_file"] = property_value
                else:
                    property_name = current_workflow.bl_rna.properties[property_name].name  # Node title
                    error_message = f"Input {property_name} is empty."
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}

            # Custom handling for image input
            elif node["class_type"] == "BlenderInputLoadImage":
                property_value = getattr(current_workflow, property_name)
                if property_value:
                    workflow[key]["inputs"]["image"] = property_value
                else:
                    property_name = current_workflow.bl_rna.properties[property_name].name  # Node title
                    error_message = f"Input {property_name} is empty."
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}

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
        response = requests.post(url, json=data, headers=headers)

        # Raise an exception for bad status codes
        if response.status_code != 200:
            error_message = response.text
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        response_data = response.text
        prompt_id = json.loads(response_data).get("prompt_id", "")
        self.report({'INFO'}, "Workflow sent to ComfyUI server.")

        # Add the prompt to the queue collection
        prompt = addon_prefs.queue.add()
        prompt.name = prompt_id
        prompt.workflow = str(workflow)
        prompt.outputs = str(outputs)
        prompt.status = "pending"

        # Start the WebSocket listener in a separate thread
        listener_thread = threading.Thread(target=connection.listen, args=(), daemon=True)
        listener_thread.start()
        self.report({'INFO'}, "WebSocket listener started.")
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRunWorkflow)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRunWorkflow)

"""Operator to send and execute a workflow on ComfyUI server."""
import json
import os
import random
import requests
import threading
from urllib.parse import urljoin

import bpy

from .. import connection
from .. import workflow as w
from ..utils import upload_file, show_error_popup


class ComfyBlenderOperatorRunWorkflow(bpy.types.Operator):
    """Operator to send and execute a workflow on ComfyUI server."""

    bl_idname = "comfy.run_workflow"
    bl_label = "Run Workflow"
    bl_description = "Send the workflow to the ComfyUI server"

    def execute(self, context):
        """Execute the operator."""

        # Get the selected workflow
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_filename)

        # Load the workflow JSON file
        if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
            with open(workflow_path, "r",  encoding="utf-8") as file:
                workflow = json.load(file)

            # Get inputs and outputs from the workflow
            inputs = w.parse_workflow_for_inputs(workflow)
            outputs = w.parse_workflow_for_outputs(workflow)

            current_workflow = context.scene.current_workflow
            for key, node in inputs.items():
                property_name = f"node_{key}"

                # Custom handling for image inputs
                if node["class_type"] == "BlenderInputLoadImage":
                    # Upload image to ComfyUI server
                    image_path = getattr(current_workflow, property_name)
                    try:
                        response = upload_file(image_path, type="image")
                        if response.status_code != 200:
                            error_message = f"Failed to upload image: {response.status_code} - {response.text}"
                            show_error_popup(error_message)
                            return {'CANCELLED'}
                    except Exception as e:
                        input_name = current_workflow.bl_rna.properties[property_name].name  # Node title
                        error_message = f"Error uploading image for input {input_name}: {str(e)}"
                        show_error_popup(error_message)
                        return {'CANCELLED'}

                    self.report({'INFO'}, "Image uploaded to ComfyUI server.")
                    image_filename = response.json()["name"]
                    workflow[key]["inputs"]["image"] = image_filename

                # Custom handling for seed inputs
                elif node["class_type"] == "BlenderInputSeed":
                    if addon_prefs.lock_seed:
                        seed = getattr(current_workflow, property_name)
                    else:
                        # If lock seed is not enabled, generate a random seed
                        min = current_workflow.bl_rna.properties[property_name].hard_min
                        max = current_workflow.bl_rna.properties[property_name].hard_max
                        seed = random.randint(min, max)
                        setattr(current_workflow, property_name, seed)
                    workflow[key]["inputs"]["value"] = seed

                else:
                    # Default handling for other input types
                    workflow[key]["inputs"]["value"] = getattr(current_workflow, property_name)

            # Establish the WebSocket connection
            if not connection.WS_CONNECTION:
                self.report({'INFO'}, "Connecting to server...")
                connection.connect()
                self.report({'INFO'}, "Connection established.")

            # Send workflow to ComfyUI server
            data = {"prompt": workflow, "client_id": addon_prefs.client_id}
            url = urljoin(addon_prefs.server_address, "/prompt")
            headers = {"Content-Type": "application/json"}

            # Create and send the request
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            response_data = response.text
            prompt_id = json.loads(response_data).get("prompt_id", "")
            self.report({'INFO'}, "Workflow sent to ComfyUI server.")

            # Add the prompt to the queue collection
            prompt = addon_prefs.queue.add()
            prompt.name = prompt_id
            prompt.workflow = str(workflow)
            prompt.outputs = str(outputs)

            # Start the WebSocket listener in a separate thread
            # listener_thread = threading.Thread(target=connection.listen, args=(workflow, prompt_id), daemon=True)
            listener_thread = threading.Thread(target=connection.listen, args=(), daemon=True)
            listener_thread.start()
            self.report({'INFO'}, "WebSocket listener started.")
        
        else:
            error_message = "Invalid workflow."
            show_error_popup(error_message)
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRunWorkflow)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRunWorkflow)

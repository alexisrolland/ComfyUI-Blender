"""Operator to send and execute a workflow on ComfyUI server."""
import json
import os
import urllib.request
import threading

import bpy

from .. import connection
from .. import workflow as w
from ..utils import upload_file


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

            # Get inputs from the workflow
            inputs = w.parse_workflow_for_inputs(workflow)

            current_workflow = context.scene.current_workflow
            for key, node in inputs.items():
                property_name = f"node_{key}"

                # Custom handling for image inputs
                if node["class_type"] == "BlenderInputLoadImage":
                    # Upload image to ComfyUI server
                    image_path = getattr(current_workflow, property_name)
                    response = upload_file(image_path, type="image")

                    if response.status_code != 200:
                        self.report({'ERROR'}, f"Failed to upload image: {response.status_code} - {response.text}")
                        return {'CANCELLED'}

                    self.report({'INFO'}, "Image uploaded to ComfyUI server.")
                    image_filename = response.json()["name"]
                    workflow[key]["inputs"]["image"] = image_filename

                else:
                    # Default handling for other input types
                    workflow[key]["inputs"]["value"] = getattr(current_workflow, property_name)

            # Establish the WebSocket connection
            self.report({'INFO'}, "Connecting to server...")
            connection.connect()
            self.report({'INFO'}, "Connection established.")

            # Send workflow to ComfyUI server
            client_id = addon_prefs.client_id
            data = {"prompt": workflow, "client_id": client_id}
            data = json.dumps(data).encode("utf-8")
            url = addon_prefs.server_address + "/prompt"
            headers = {"Content-Type": "application/json"}

            # Create a request object and send it
            request = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(request) as r:
                response_status = r.status
                response_message = r.reason
                response_data = r.read().decode("utf-8")

            if response_status != 200:
                self.report({'ERROR'}, f"Failed to send workflow: {response_status} - {response_message}")
                return {'CANCELLED'}

            self.report({'INFO'}, "Workflow sent to ComfyUI server.")
            prompt_id = json.loads(response_data).get("prompt_id", "")

            # Start the WebSocket listener in a separate thread
            listener_thread = threading.Thread(target=connection.listen, args=(workflow, prompt_id), daemon=True)
            listener_thread.start()
            self.report({'INFO'}, "WebSocket listener started.")
        
        else:
            self.report({'ERROR'}, "Invalid workflow.")
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRunWorkflow)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRunWorkflow)

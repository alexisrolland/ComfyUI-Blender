"""Operator to send and execute a workflow on ComfyUI server."""
import json
import os
import re
import requests
import threading

import bpy

from .. import connection
from .. import workflow as w


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
        workflow_file = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_file)
        workflow_name = os.path.splitext(os.path.basename(workflow_path))[0]

        # Load the workflow JSON file
        if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
            with open(workflow_path, "r",  encoding="utf-8") as f:
                workflow = json.load(f)

            # Get inputs from the workflow
            # This function filters nodes with 'class_type' starting with 'BlenderInput...'
            inputs = w.parse_workflow_for_inputs(workflow)

            current_workflow = context.scene.current_workflow
            for key in inputs:
                property_name = f"node_{key}"
                workflow[key]["inputs"]["value"] = getattr(current_workflow, property_name)

            # Establish the WebSocket connection
            self.report({'INFO'}, "Connecting to server...")
            connection.connect()
            self.report({'INFO'}, "Connection established.")

            # Send workflow to ComfyUI server
            client_id = addon_prefs.client_id
            payload = {"prompt": workflow, "client_id": client_id}
            server_address = addon_prefs.server_address
            response = requests.post(server_address + "/prompt", json=payload)

            if response.status_code != 200:
                self.report({'ERROR'}, f"Failed to send workflow: {response.status_code} - {response.text}")
                return {'CANCELLED'}

            self.report({'INFO'}, "Workflow sent to ComfyUI server.")
            prompt_id = response.json().get("prompt_id", "")

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

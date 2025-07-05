import bpy
import json
import os
import requests
import threading
from .. import connection

class COMFY_OT_RunWorkflow(bpy.types.Operator):
    """Operator to update the workflow JSON file and send it to the ComfyUI server."""
    bl_idname = "comfy.run_workflow"
    bl_label = "Run Workflow"
    bl_description = "Send the workflow to the ComfyUI server"

    def execute(self, context):
        # Get the selected workflow
        selected_workflow = context.scene.workflow
        if not selected_workflow:
            self.report({'ERROR'}, "No workflow selected.")
            return {'CANCELLED'}

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflow_folder = addon_prefs.workflow_folder
        workflow_path = os.path.join(workflow_folder, selected_workflow)
        workflow_name = os.path.splitext(os.path.basename(workflow_path))[0]

        # Load the workflow JSON file
        try:
            with open(workflow_path, "r") as f:
                workflow = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load workflow: {e}")
            return {'CANCELLED'}

        # Update the workflow with values from the panel
        for key in workflow.keys():
            input = f"wkf_{workflow_name}_{key}"
            if input in context.scene.keys():
                workflow[key]["inputs"]["value"] = getattr(bpy.context.scene, input, None)

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
        
        self.report({'INFO'}, "Workflow sent successfully.")
        prompt_id = response.json().get("prompt_id", "")

        # Start the WebSocket listener in a separate thread
        listener_thread = threading.Thread(target=connection.listen, args=(workflow, prompt_id), daemon=True)
        listener_thread.start()
        self.report({'INFO'}, "WebSocket listener started.")

        return {'FINISHED'}

def register():
    bpy.utils.register_class(COMFY_OT_RunWorkflow)

def unregister():
    bpy.utils.unregister_class(COMFY_OT_RunWorkflow)
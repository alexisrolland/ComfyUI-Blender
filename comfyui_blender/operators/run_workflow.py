import bpy
import os
import json
import requests

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
                workflow_data = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load workflow: {e}")
            return {'CANCELLED'}

        # Update the workflow with panel values
        for key in workflow_data.keys():
            input = f"wkf_{workflow_name}_{key}"
            if input in context.scene.keys():
                workflow_data[key]["inputs"]["value"] = getattr(bpy.context.scene, input, None)

        # Get the server URL from addon preferences
        server_address = addon_prefs.server_address
        client_id = context.scene.client_id

        # Send the workflow to the ComfyUI server
        try:
            payload = { "prompt": workflow_data, "client_id": client_id }
            response = requests.post(server_address + "/prompt", json=payload)
            if response.status_code == 200:
                self.report({'INFO'}, "Workflow sent successfully.")
                context.scene.prompt_id = response.json().get("prompt_id", "")
            else:
                self.report({'ERROR'}, f"Failed to send workflow: {response.status_code} - {response.text}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to send workflow: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    bpy.utils.register_class(COMFY_OT_RunWorkflow)

def unregister():
    bpy.utils.unregister_class(COMFY_OT_RunWorkflow)
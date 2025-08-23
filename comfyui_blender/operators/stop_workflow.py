"""Operator to stop the execution of a workflow on ComfyUI server."""
import logging
import requests

import bpy

from ..utils import add_custom_headers, get_server_url

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorStopWorkflow(bpy.types.Operator):
    """Operator to stop the execution of a workflow on ComfyUI server."""

    bl_idname = "comfy.stop_workflow"
    bl_label = "Stop Workflow"
    bl_description = "Stop the current workflow execution on the ComfyUI server"

    def execute(self, context):
        """Execute the operator."""

        # Get add-on preferences
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences

        # Send stop workflow execution to ComfyUI server
        url = get_server_url("/interrupt")
        headers = {"Content-Type": "application/json"}
        headers = add_custom_headers(headers)
        try:
            response = requests.post(url, json={}, headers=headers)
        except Exception as e:
            error_message = f"Failed to send stop workflow request to ComfyUI server: {addon_prefs.server_address}. {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        if response.status_code != 200:
            error_message = response.text
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        self.report({'INFO'}, "Request to stop workflow execution sent to ComfyUI server.")
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorStopWorkflow)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorStopWorkflow)

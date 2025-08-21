"""Operator to stop the execution of a workflow on ComfyUI server."""
import requests

import bpy

from ..utils import add_custom_headers, get_server_url


class ComfyBlenderOperatorStopWorkflow(bpy.types.Operator):
    """Operator to stop the execution of a workflow on ComfyUI server."""

    bl_idname = "comfy.stop_workflow"
    bl_label = "Stop Workflow"
    bl_description = "Stop the current workflow execution on the ComfyUI server"

    def execute(self, context):
        """Execute the operator."""

        # Stop workflow execution on ComfyUI server
        url = get_server_url("/interrupt")
        headers = {"Content-Type": "application/json"}
        headers = add_custom_headers(headers)
        response = requests.post(url, json={}, headers=headers)

        # Raise an exception for bad status codes
        if response.status_code != 200:
            error_message = response.text
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

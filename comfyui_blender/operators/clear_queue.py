"""Operator to remove all pending workflows from ComfyUI server queue."""
import requests
from urllib.parse import urljoin

import bpy

from ..utils import add_comfy_headers, get_url, show_error_popup


class ComfyBlenderOperatorStopWorkflow(bpy.types.Operator):
    """Operator to remove all pending workflows from ComfyUI server queue."""

    bl_idname = "comfy.clear_queue"
    bl_label = "Clear Queue"
    bl_description = "Remove all pending workflows from ComfyUI server queue"

    def execute(self, context):
        """Execute the operator."""

        # Get add-on preferences
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences

        # Stop workflow execution on ComfyUI server
        data = {"clear": True}
        url = get_url("/queue")
        headers = {"Content-Type": "application/json"}
        headers = add_comfy_headers(headers)
        response = requests.post(url, json=data, headers=headers)

        # Raise an exception for bad status codes
        if response.status_code != 200:
            error_message = response.text
            show_error_popup(error_message)
            return {'CANCELLED'}

        # Get indices of workflows to remove and remove them in reverse order
        queue = addon_prefs.queue
        workflow_indices = [i for i, workflow in enumerate(queue) if workflow.status == "pending"]
        for i in reversed(workflow_indices):
            queue.remove(i)

        self.report({'INFO'}, "Request to stop workflow execution sent to ComfyUI server.")
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorStopWorkflow)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorStopWorkflow)

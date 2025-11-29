"""Operator to download workflows from ComfyUI server."""
import json
import logging
import requests

import bpy

from ..utils import (
    add_custom_headers,
    get_filepath,
    get_server_url,
    get_workflows_folder
)
from ..workflow import check_workflow_file_exists

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorDownloadWorkflows(bpy.types.Operator):
    """Operator to download workflows from ComfyUI server."""

    bl_idname = "comfy.download_workflows"
    bl_label = "Download Workflows"
    bl_description = "Download workflows from the ComfyUI server."

    def execute(self, context):
        """Execute the operator."""

        # Get the list of workflows
        url = get_server_url("/blender/workflows")
        headers = add_custom_headers()
        try:
            response = requests.get(url, headers=headers)
            workflows = response.json()
        except Exception as e:
            addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
            error_message = f"Failed to get list of workflows from ComfyUI server: {addon_prefs.server_address}. {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Download workflows in API format
        for workflow in workflows:
            workflow_name = workflow["name"]
            workflow_path = workflow["path"]
            url = get_server_url(f"/blender/workflow")
            url = url + f"?filepath={workflow_path}"
            try:
                response = requests.get(url, headers=headers)
            except Exception as e:
                addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
                error_message = f"Failed to download workflow from ComfyUI server: {addon_prefs.server_address}. {e}"
                log.exception(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            if response.status_code != 200:
                error_message = f"Failed to download workflow from ComfyUI server: {url}"
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                continue

            self.report({'INFO'}, f"Downloaded workflow: {workflow_path}")
            # Check if a workflow with the same data already exists
            workflow_data = response.json()
            workflows_folder = get_workflows_folder()
            workflow_filename = check_workflow_file_exists(workflow_data, workflows_folder)

            # Get target file name and path if workflow does not exist
            if not workflow_filename:
                workflow_filename, workflow_path = get_filepath(workflow_name, workflows_folder)

                try:
                    # Save the file to the workflow folder
                    with open(workflow_path, "w", encoding="utf-8") as file:
                        json.dump(workflow_data, file, indent=2, ensure_ascii=False)
                    self.report({'INFO'}, f"Workflow saved to: {workflow_path}")
                except Exception as e:
                    error_message = f"Failed to save workflow: {e}"
                    log.exception(error_message)
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue
            else:
                self.report({'INFO'}, f"Workflow already exists: {workflow_filename}")

            # Force refresh of the panel
            addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
            if addon_prefs.workflow:
                addon_prefs.workflow = addon_prefs.workflow
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDownloadWorkflows)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDownloadWorkflows)

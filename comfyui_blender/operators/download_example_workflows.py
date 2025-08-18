"""Operator to download example workflows from ComfyUI server."""
import json
import logging
import requests

import bpy

from ..utils import add_custom_headers, get_filepath, get_server_url
from ..workflow import check_workflow_file_exists

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorDownloadExampleWorkflows(bpy.types.Operator):
    """Operator to download example workflows from ComfyUI server."""

    bl_idname = "comfy.download_example_workflows"
    bl_label = "Download Example Workflows"
    bl_description = "Download example workflows from the ComfyUI server"

    # If the custom node name has been changed on the ComfyUI server, we won't be able to download workflows.
    custom_node_name = "ComfyUI-Blender"

    def execute(self, context):
        """Execute the operator."""
        
        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)

        # Download example workflows
        url = get_server_url("/api/workflow_templates")
        headers = add_custom_headers()
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            error_message = f"Failed to download example workflows from ComfyUI server: {addon_prefs.server_address}. {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Find matching key case-insensitively
        workflow_templates = response.json()
        custom_node_key = next((k for k in workflow_templates.keys() if k.casefold() == self.custom_node_name.casefold()), None)
        example_workflows = workflow_templates.get(custom_node_key, []) if custom_node_key else []
        if not example_workflows:
            error_message = f"Example workflows not found. The ComfyUI-Blender nodes may not be properly installed on the ComfyUI server."
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Download workflows
        for workflow in example_workflows:
            self.report({'INFO'}, f"Downloading workflow: {workflow}")
            url = get_server_url(f"/api/workflow_templates/{custom_node_key}/{workflow}.json.api")
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                error_message = f"Failed to download workflow: {url}"
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                continue

            # Check if a workflow with the same data already exists
            workflow_data = response.json()
            workflow_filename = check_workflow_file_exists(workflow_data, workflows_folder)

            # Get target file name and path if workflow does not exist
            if not workflow_filename:
                workflow_filename = workflow + ".json"
                workflow_filename, workflow_path = get_filepath(workflow_filename, workflows_folder)

                try:
                    # Save the file to the workflow folder
                    with open(workflow_path, "w", encoding="utf-8") as file:
                        json.dump(workflow_data, file, indent=2, ensure_ascii=False)
                    self.report({'INFO'}, f"Workflow saved to: {workflow_path}")

                except Exception as e:
                    error_message = f"Failed to save workflow: {e}"
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    continue
            else:
                self.report({'INFO'}, f"Workflow already exists: {workflow_filename}")

            # Force refresh of the panel
            addon_prefs.workflow = addon_prefs.workflow
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDownloadExampleWorkflows)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDownloadExampleWorkflows)

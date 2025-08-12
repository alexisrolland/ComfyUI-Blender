"""Operator to download example workflows from ComfyUI server."""
import json
import logging
import os
import requests
import shutil
from urllib.parse import urljoin, quote

import bpy

from ..utils import get_filepath, show_error_popup

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorDownloadExampleWorkflows(bpy.types.Operator):
    """Operator to download example workflows from ComfyUI server."""

    bl_idname = "comfy.download_example_workflows"
    bl_label = "Download Example Workflows"
    bl_description = "Download ComfyUI-Blender example workflows from the ComfyUI server"
    custom_node_name = "ComfyUI-Blender"

    def execute(self, context):
        """
        List the ComfyUI_blender addon example workflows to be able to run them directly from Blender
        If custom_node name has been changed we won't be able to fetch the workflows.
        """
        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        server_address = addon_prefs.server_address
        workflow_templates_url = urljoin(server_address, "/api/workflow_templates")

        workflow_templates = requests.get(workflow_templates_url).json()
        # Find matching key case-insensitively
        custom_node_key = next((k for k in workflow_templates.keys() if k.casefold() == self.custom_node_name.casefold()), None)
        blender_workflows = workflow_templates.get(custom_node_key, []) if custom_node_key else []
        if not blender_workflows:
            log.warning(f"No ComfyUI-Blender workflow found. custom_node may not be properly installed.")
            return

        workflows_folder = str(addon_prefs.workflows_folder)
        os.makedirs(workflows_folder, exist_ok=True)

        for workflow in blender_workflows:
            try:
                log.info(f"Downloading workflow: {workflow}")
                workflow_download_url = urljoin(server_address, quote(f"/api/workflow_templates/{self.custom_node_name}/{workflow}.json.api"))
                workflow_json = requests.get(workflow_download_url).json()

                workflow_path = os.path.join(workflows_folder, f"{self.custom_node_name}-{workflow}.json")
                with open(workflow_path, "w+") as f:
                    json.dump(workflow_json, f)
                    self.report({'INFO'}, f"Workflow {workflow} saved as: {workflow_path}")
                # Get target file name and path
                workflow_filename, workflow_path = get_filepath(workflow, workflows_folder)

            except Exception as e:
                error_message = f"Failed fetching workflow {workflow}: {e}"
                log.error(error_message)
                show_error_popup(error_message)

        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDownloadExampleWorkflows)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDownloadExampleWorkflows)

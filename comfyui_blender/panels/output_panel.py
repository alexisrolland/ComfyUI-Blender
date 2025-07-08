"""Panel to display generated outputs."""
import os
import json

import bpy

from .. import workflow as w


class ComfyBlenderPanelOutput(bpy.types.Panel):
    """Panel to display generated outputs."""

    bl_label = "Outputs"
    bl_idname = "COMFY_PT_Output"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="IMAGE_DATA")

    def draw(self, context):
        """Draw the panel."""

        # Open file browser
        layout = self.layout
        layout.operator("comfy.open_file_browser", text="Open Outputs Folder")        

        # Get the selected workflow
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_file = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_file)

        # Load the workflow JSON file
        if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
            box = layout.box()
            with open(workflow_path, "r",  encoding="utf-8") as f:
                workflow = json.load(f)

            # Get outputs from the workflow
            outputs = w.parse_workflow_for_outputs(workflow)
            outputs_folder = str(addon_prefs.outputs_folder)

            # Display workflow output properties
            if hasattr(context.scene, "current_workflow"):
                current_workflow = context.scene.current_workflow
                for key, node in outputs.items():
                    # Image output
                    if node["class_type"] == "BlenderOutputSaveImage":
                        filepath = getattr(current_workflow, f"node_{key}")
                        filepath = os.path.join(outputs_folder, filepath)
                        filename = os.path.basename(filepath)
                        if os.path.exists(filepath):
                            if filename not in bpy.data.images:
                                bpy.data.images.load(filepath, check_existing=True)
                            if filename in bpy.data.images:
                                bpy.data.images[filename].preview_ensure()
                                box.template_icon(icon_value=bpy.data.images[filename].preview.icon_id, scale=5)

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelOutput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelOutput)

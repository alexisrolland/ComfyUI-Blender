"""Panel to display a workflow inputs."""
import json
import os

import bpy

from .. import workflow as w


class ComfyBlenderPanelInput(bpy.types.Panel):
    """Panel to display a workflow inputs."""

    bl_label = "Inputs"
    bl_idname = "COMFY_PT_Input"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="EXPERIMENTAL")

    def draw(self, context):
        """Draw the panel."""

        layout = self.layout

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

            # Get sorted inputs from the workflow
            inputs = w.parse_workflow_for_inputs(workflow)

            # Display workflow input properties
            if hasattr(context.scene, "current_workflow"):
                current_workflow = context.scene.current_workflow
                for key in inputs:
                    box.prop(current_workflow, f"node_{key}")
                box.operator("comfy.run_workflow", text="Run Workflow")

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelInput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelInput)

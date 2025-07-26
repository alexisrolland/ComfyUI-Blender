"""Panel to display workflows."""
import os

import bpy


class ComfyBlenderPanelWorkflow(bpy.types.Panel):
    """Panel to display workflows."""

    bl_label = "Workflow"
    bl_idname = "COMFY_PT_Workflow"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="NODETREE")

    def draw(self, context):
        """Draw the panel."""

        # Buttons to open preferences
        row = self.layout.row()
        row.alignment = "RIGHT"
        row.operator("preferences.addon_show", text="", icon="PREFERENCES").module = "comfyui_blender"

        # Get workflows information
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_filename)

        # Buttons to import a workflow
        row = self.layout.row(align=True)
        row.operator("comfy.import_workflow", text="Import Workflow")
        row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER_LARGE").folder_path = workflows_folder

        # Dropdown list of workflows with actions
        row = self.layout.row(align=True)
        row.prop(addon_prefs, "workflow")
        delete_workflow = row.operator("comfy.delete_workflow", text="", icon="TRASH")
        delete_workflow.filename = workflow_filename
        delete_workflow.filepath = workflow_path

        # Queue status and progress bar
        row = self.layout.row(align=True)
        split = row.split(factor=0.23)
        split.label(text=f"Queue: {len(addon_prefs.queue)}")
        split.progress(factor=addon_prefs.progress_value, text=f"{int(addon_prefs.progress_value * 100)}%", type="BAR")
        if addon_prefs.connection_status:
            row.label(icon="INTERNET")
        else:
            row.label(icon="INTERNET_OFFLINE")

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelWorkflow)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelWorkflow)

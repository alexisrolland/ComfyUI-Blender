"""Panel to display workflows."""
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

        layout = self.layout

        # Buttons to open preferences
        row = layout.row()
        row.label(text="") # Empty label for spacing
        row.operator("preferences.addon_show", text="", icon="PREFERENCES").module = "comfyui_blender"

        # Get workflows information
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)

        # Buttons to import a workflow
        row = layout.row(align=True)
        row.operator("comfy.import_workflow", text="Import Workflow")
        row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER_LARGE").folder_path = workflows_folder

        # Dropdown list of workflows with actions
        row = layout.row(align=True)
        row.prop(addon_prefs, "workflow")
        row.operator("comfy.delete_workflow", text="", icon="TRASH").filename = workflow_filename

        # Queue status
        queue = addon_prefs.queue
        connection_status = addon_prefs.connection_status
        row = layout.row()
        if connection_status:
            row.label(text=f"Queue: {queue}")
            row.label(icon="SORTTIME")
        else:
            row.label(text=f"Queue: {queue}")

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelWorkflow)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelWorkflow)

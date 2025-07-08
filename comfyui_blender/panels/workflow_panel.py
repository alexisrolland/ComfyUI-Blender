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

        # Buttons to import a workflow and show add-on preferences
        row = layout.row()
        row.operator("comfy.import_workflow", text="Import Workflow")
        row.operator("preferences.addon_show", icon="PREFERENCES").module = "comfyui_blender"

        # Dropdown list of workflows
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        layout.prop(addon_prefs, "workflow")

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

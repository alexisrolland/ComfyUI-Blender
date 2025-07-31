"""Operator to delete a workflow JSON file."""
import os

import bpy

from ..workflow import get_workflow_list
from ..utils import show_error_popup


class ComfyBlenderOperatorDeleteWorkflow(bpy.types.Operator):
    """Operator to delete a workflow JSON file."""

    bl_idname = "comfy.delete_workflow"
    bl_label = "Delete Workflow"
    bl_description = "Delete a workflow JSON file from the workflows folder"

    filename: bpy.props.StringProperty(name="File Name")
    filepath: bpy.props.StringProperty(name="File Path")

    def execute(self, context):
        """Execute the operator."""

        return {'FINISHED'}

    def invoke(self, context, event):
        """Show a confirmation dialog box."""

        # Use invoke popup instead invoke props dialog to avoid blocking thread
        # Invoke popup requires a custom OK / Cancel buttons
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        """Customize the confirmation dialog."""

        layout = self.layout

        # Title
        row = layout.row()
        row.label(text="Delete Workflow")
        layout.separator(type="LINE")

        # Message
        col = layout.column(align=True)
        col.label(text="Are you sure you want to delete:")
        col.label(text=f"{self.filename}?")

        # Buttons
        row = layout.row()
        button_ok = row.operator("comfy.delete_workflow_ok", text="OK", depress=True)
        button_ok.filename = self.filename
        button_ok.filepath = self.filepath
        row.operator("comfy.delete_workflow_cancel", text="Cancel")

class ComfyBlenderOperatorDeleteWorkflowOk(bpy.types.Operator):
    """Confirm deletion."""

    bl_idname = "comfy.delete_workflow_ok"
    bl_label = "Confirm Delete"
    bl_description = "Confirm the deletion of the workflow."
    bl_options = {'INTERNAL'}

    filename: bpy.props.StringProperty(name="File Name")
    filepath: bpy.props.StringProperty(name="File Path")

    def execute(self, context):
        """Execute the operator."""

        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
                self.report({'INFO'}, f"Deleted workflow: {self.filepath}")
                
                # Get the updated workflow list and set to first workflow
                addon_prefs = context.preferences.addons["comfyui_blender"].preferences
                workflows = get_workflow_list(addon_prefs, context)
                addon_prefs.workflow = workflows[0][0]  # First tuple's first element (filename)
            else:
                self.report({'WARNING'}, f"Workflow file not found: {self.filepath}")
                return {'CANCELLED'}

        except Exception as e:
            error_message = f"Failed to delete workflow {self.filepath}: {str(e)}"
            show_error_popup(error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

class ComfyBlenderOperatorDeleteWorkflowCancel(bpy.types.Operator):
    """Cancel deletion."""

    bl_idname = "comfy.delete_workflow_cancel"
    bl_label = "Cancel Delete"
    bl_description = "Cancel the deletion of the workflow."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        """Execute the operator."""

        return {'CANCELLED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDeleteWorkflow)
    bpy.utils.register_class(ComfyBlenderOperatorDeleteWorkflowOk)
    bpy.utils.register_class(ComfyBlenderOperatorDeleteWorkflowCancel)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteWorkflow)
    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteWorkflowOk)
    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteWorkflowCancel)

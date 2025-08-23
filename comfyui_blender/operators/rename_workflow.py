"""Operator to rename a workflow file."""
import logging
import os

import bpy

from ..utils import get_filepath

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorRenameWorkflow(bpy.types.Operator):
    """Operator to rename a workflow file."""

    bl_idname = "comfy.rename_workflow"
    bl_label = "Rename Workflow"
    bl_description = "Rename the workflow file."

    current_filename: bpy.props.StringProperty(name="Current File Name")
    new_filename: bpy.props.StringProperty(name="New File Name")

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
        row.label(text="Rename Workflow")
        layout.separator(type="LINE")

        # Form
        col = layout.column(align=True)
        col.prop(self, "new_filename")

        # Buttons
        row = layout.row()
        button_ok = row.operator("comfy.rename_workflow_ok", text="OK", depress=True)
        button_ok.current_filename = self.current_filename
        button_ok.new_filename = self.new_filename
        row.operator("comfy.rename_workflow_cancel", text="Cancel")


class ComfyBlenderOperatorRenameWorkflowOk(bpy.types.Operator):
    """Confirm renaming."""

    bl_idname = "comfy.rename_workflow_ok"
    bl_label = "Confirm Rename"
    bl_description = "Confirm the renaming of the workflow."
    bl_options = {'INTERNAL'}

    current_filename: bpy.props.StringProperty(name="Current File Name")
    new_filename: bpy.props.StringProperty(name="New File Name")

    def execute(self, context):
        """Execute the operator."""

        # Get workflows folder
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        current_filepath = os.path.join(workflows_folder, self.current_filename)
        new_filename, new_filepath = get_filepath(self.new_filename, workflows_folder)

        try:
            # Rename the file
            os.rename(current_filepath, new_filepath)
            self.report({'INFO'}, f"Renamed workflow to: {new_filepath}")
        except Exception as e:
            error_message = f"Failed to rename workflow {current_filepath}: {str(e)}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Set current workflow to load workflow
        addon_prefs.workflow = new_filename
        return {'FINISHED'}


class ComfyBlenderOperatorRenameWorkflowCancel(bpy.types.Operator):
    """Cancel renaming."""

    bl_idname = "comfy.rename_workflow_cancel"
    bl_label = "Cancel Rename"
    bl_description = "Cancel the renaming of the workflow."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        """Execute the operator."""

        return {'CANCELLED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRenameWorkflow)
    bpy.utils.register_class(ComfyBlenderOperatorRenameWorkflowOk)
    bpy.utils.register_class(ComfyBlenderOperatorRenameWorkflowCancel)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRenameWorkflow)
    bpy.utils.unregister_class(ComfyBlenderOperatorRenameWorkflowOk)
    bpy.utils.unregister_class(ComfyBlenderOperatorRenameWorkflowCancel)

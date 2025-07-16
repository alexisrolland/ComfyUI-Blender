"""Operator to delete a workflow JSON file."""
import os

import bpy

from ..workflow import get_workflow_list


class ComfyBlenderOperatorDeleteWorkflow(bpy.types.Operator):
    """Operator to delete a workflow JSON file."""

    bl_idname = "comfy.delete_workflow"
    bl_label = "Delete Workflow"
    bl_description = "Delete a workflow JSON file from the workflows folder"

    filename: bpy.props.StringProperty(name="File Name")

    def execute(self, context):
        """Execute the operator."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_path = os.path.join(workflows_folder, self.filename)

        try:
            if os.path.exists(workflow_path):
                os.remove(workflow_path)
                self.report({'INFO'}, f"Deleted workflow: {workflow_path}")
                
                # Get the updated workflow list and set to first workflow
                workflows = get_workflow_list(addon_prefs, context)
                addon_prefs.workflow = workflows[0][0]  # First tuple's first element (filename)
            else:
                self.report({'WARNING'}, f"Workflow file not found: {workflow_path}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to delete workflow {workflow_path}: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        """Show a confirmation dialog box."""

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        """Customize the confirmation dialog."""

        layout = self.layout
        col = layout.column(align=True)
        col.label(text=f"Are you sure you want to delete:")
        col.label(text=f"{self.filename}?")

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDeleteWorkflow)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteWorkflow)

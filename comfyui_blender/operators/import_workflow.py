"""Operator to import a workflow JSON file."""
import os
import shutil

import bpy

from ..utils import get_filepath, show_error_popup


class ComfyBlenderOperatorImportWorkflow(bpy.types.Operator):
    """Operator to import a workflow JSON file."""

    bl_idname = "comfy.import_workflow"
    bl_label = "Import Workflow"
    bl_description = "Import a workflow JSON file"

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(name="File Filter", default="*.json")

    def execute(self, context):
        """Execute the operator."""

        if self.filepath.lower().endswith(".json"):
            addon_prefs = context.preferences.addons["comfyui_blender"].preferences
            workflows_folder = str(addon_prefs.workflows_folder)
            workflow_filename = os.path.basename(self.filepath)

            # Create the workflows folder if it doesn't exist
            os.makedirs(workflows_folder, exist_ok=True)

            # Get target file name and path
            workflow_filename, workflow_path = get_filepath(workflow_filename, workflows_folder)

            try:
                # Copy the file to the workflows folder and select the workflow
                shutil.copy(self.filepath, workflow_path)
                addon_prefs.workflow = workflow_filename
                self.report({'INFO'}, f"Workflow copied to: {workflow_path}")

            except Exception as e:
                error_message = f"Failed to copy workflow file: {e}"
                show_error_popup(error_message)
                return {'CANCELLED'}

        else:
            error_message = "Selected file is not a *.json."
            show_error_popup(error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector for importing a workflow."""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportWorkflow)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportWorkflow)

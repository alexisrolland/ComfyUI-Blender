"""Operator to import a workflow JSON file."""
import os
import shutil

import bpy


class ComfyBlenderOperatorImportWorkflow(bpy.types.Operator):
    """Operator to import a workflow JSON file."""

    bl_idname = "comfy.import_workflow"
    bl_label = "Import Workflow"
    bl_description = "Import a workflow JSON file"

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")

    def execute(self, context):
        """Execute the operator."""

        if self.filepath.endswith(".json"):
            # Get the selected workflow
            addon_prefs = context.preferences.addons["comfyui_blender"].preferences
            workflows_folder = str(addon_prefs.workflows_folder)
            workflow_file = os.path.basename(self.filepath)
            workflow_path = os.path.join(workflows_folder, workflow_file)

            # Create the workflows folder if it doesn't exist
            os.makedirs(workflows_folder, exist_ok=True)

            # Handle file name conflicts by appending an incremental number
            if os.path.exists(workflow_path):
                name, ext = os.path.splitext(workflow_file)
                counter = 1
                while os.path.exists(os.path.join(workflows_folder, f"{name}_{counter}{ext}")):
                    counter += 1
                
                # Rename workflow file
                workflow_file = f"{name}_{counter}{ext}"
                workflow_path = os.path.join(workflows_folder, workflow_file)

            try:
                # Copy the file to the workflows directory and select the workflow
                shutil.copy(self.filepath, workflow_path)
                addon_prefs.workflow = workflow_file
                self.report({'INFO'}, f"Workflow copied to: {workflow_path}")

            except Exception as e:
                self.report({'ERROR'}, f"Failed to copy workflow: {e}")

        else:
            self.report({'ERROR'}, "Selected file is not a JSON file.")
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

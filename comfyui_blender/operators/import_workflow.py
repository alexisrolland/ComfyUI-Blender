"""Operator to import a workflow JSON file."""
import json
import logging
import os
import shutil

import bpy

from ..utils import get_filepath
from ..workflow import check_workflow_file_exists, extract_workflow_from_metadata

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorImportWorkflow(bpy.types.Operator):
    """Operator to import a workflow JSON file."""

    bl_idname = "comfy.import_workflow"
    bl_label = "Import Workflow"
    bl_description = "Import a workflow JSON file."

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(name="File Filter", default="*.glb;*.json;*.png;")
    invoke_default: bpy.props.BoolProperty(default=True, options={'HIDDEN'})

    def execute(self, context):
        """Execute the operator."""

        # Get workflows folder
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)

        # Import workflow from JSON file
        if self.filepath.lower().endswith(".json"):
            with open(self.filepath, "r", encoding="utf-8") as file:
                new_workflow_data = json.load(file)

            # Check if a workflow with the same data already exists
            workflow_filename = check_workflow_file_exists(new_workflow_data, workflows_folder)

            # Get target file name and path if workflow does not exist
            if not workflow_filename:
                workflow_filename = os.path.basename(self.filepath)
                workflow_filename, workflow_path = get_filepath(workflow_filename, workflows_folder)
                try:
                    # Copy the file to the workflows folder
                    shutil.copy(self.filepath, workflow_path)
                    self.report({'INFO'}, f"Workflow copied to: {workflow_path}")
                except shutil.SameFileError as e:
                    self.report({'INFO'}, f"Workflow is already in the inputs folder: {workflow_path}")
                except Exception as e:
                    error_message = f"Failed to copy workflow file: {e}"
                    log.exception(error_message)
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}
            else:
                self.report({'INFO'}, f"Workflow already exists: {workflow_filename}")

            # Set current workflow to load workflow
            addon_prefs.workflow = workflow_filename

        # Import workflow from output files
        elif self.filepath.lower().endswith((".glb", ".png")):
            # Extract workflow from the metadata of the file
            new_workflow_data = extract_workflow_from_metadata(self.filepath)
            if not new_workflow_data:
                error_message = "No workflow found in the metadata."
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            # Check if a workflow with the same data already exists
            workflow_filename = check_workflow_file_exists(new_workflow_data, workflows_folder)

            # Get target file name and path if workflow does not exist
            if not workflow_filename:
                workflow_filename = os.path.basename(self.filepath)
                workflow_filename = os.path.splitext(workflow_filename)[0] + ".json"
                workflow_filename, workflow_path = get_filepath(workflow_filename, workflows_folder)
                try:
                    # Save the file to the workflow folder
                    with open(workflow_path, "w", encoding="utf-8") as file:
                        json.dump(new_workflow_data, file, indent=2, ensure_ascii=False)
                    self.report({'INFO'}, f"Workflow saved to: {workflow_path}")
                except Exception as e:
                    error_message = f"Failed to save workflow: {e}"
                    log.exception(error_message)
                    bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                    return {'CANCELLED'}
            else:
                self.report({'INFO'}, f"Workflow already exists: {workflow_filename}")

            # Set current workflow to load workflow
            addon_prefs.workflow = workflow_filename

        else:
            error_message = "Selected file extension is not supported."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector."""

        # Skip modal box
        if not self.invoke_default:
            return self.execute(context)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportWorkflow)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportWorkflow)

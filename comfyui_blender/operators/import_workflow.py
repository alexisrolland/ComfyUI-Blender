"""Operator to import a workflow JSON file."""
import json
import logging
import os
import shutil

import bpy

from ..utils import contains_non_latin, get_filepath, get_workflows_folder
from ..workflow import check_workflow_file_exists, extract_workflow_from_metadata

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorImportWorkflow(bpy.types.Operator):
    """Operator to import a workflow JSON file."""

    bl_idname = "comfy.import_workflow"
    bl_label = "Import Workflow"
    bl_description = "Import a workflow from a JSON file or from the metadata of an output file."

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    directory: bpy.props.StringProperty(name="Directory", subtype="DIR_PATH")
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    filter_glob: bpy.props.StringProperty(name="File Filter", default="*.glb;*.json;*.png;")
    invoke_default: bpy.props.BoolProperty(default=True, options={'HIDDEN'})

    def execute(self, context):
        """Execute the operator."""

        # Get workflows folder
        workflows_folder = get_workflows_folder()

        # Build list of selected files paths
        selected_files = []
        if getattr(self, "files", None) and len(self.files) > 0:
            for file in self.files:
                # Check for non-latin characters in file name
                # Non-latin characters cause issues with Blender dropdown menus
                if not contains_non_latin(file.name):
                    selected_files.append(os.path.join(self.directory, file.name))
                else:
                    self.report({'ERROR'}, f"Could not import workflow. File name contains non-latin characters: {file.name}")
                    log.error(f"Could not import workflow. File name contains non-latin characters: {file.name}")
        elif self.filepath:
            # Check for non-latin characters in file name
            # Non-latin characters cause issues with Blender dropdown menus
            filename = os.path.basename(self.filepath)
            if not contains_non_latin(filename):
                selected_files.append(self.filepath)
            else:
                self.report({'ERROR'}, f"Could not import workflow. File name contains non-latin characters: {filename}")
                log.error(f"Could not import workflow. File name contains non-latin characters: {filename}")
            selected_files.append(self.filepath)
        else:
            self.report({'ERROR'}, "No file selected.")
            return {'CANCELLED'}

        import_failures = 0
        for path in selected_files:
            try:
                # Import workflow
                workflow_filename = self.process_single_file(workflows_folder, path)

                # Set current workflow to workflow
                addon_prefs = context.preferences.addons["comfyui_blender"].preferences
                addon_prefs.workflow = workflow_filename
            except Exception as e:
                error_message = str(e)
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                import_failures += 1
                continue

        # Clear selected files for the next run
        self.files.clear()
        return {'CANCELLED'} if import_failures > 0 else {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector."""

        # Skip modal box
        if not self.invoke_default:
            return self.execute(context)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def process_single_file(self, workflows_folder, path):
        """Process file to import workflow."""

        # Import workflow from JSON file
        if path.lower().endswith(".json"):
            with open(path, "r", encoding="utf-8") as file:
                new_workflow_data = json.load(file)

            # Check if a workflow with the same data already exists
            workflow_filename = check_workflow_file_exists(new_workflow_data, workflows_folder)

            # Get target file name and path if workflow does not exist
            if not workflow_filename:
                workflow_filename = os.path.basename(path)
                workflow_filename, workflow_path = get_filepath(workflow_filename, workflows_folder)
                try:
                    # Copy the file to the workflows folder
                    shutil.copy(path, workflow_path)
                    self.report({'INFO'}, f"Workflow copied to: {workflow_path}")
                    return workflow_filename
                except shutil.SameFileError as e:
                    self.report({'INFO'}, f"Workflow is already in the inputs folder: {workflow_path}")
                except Exception as e:
                    error_message = f"Failed to copy workflow file {path}: {e}"
                    raise Exception(error_message)
            else:
                self.report({'INFO'}, f"Workflow already exists: {workflow_filename}")
                return workflow_filename

        # Import workflow from output files
        elif path.lower().endswith((".glb", ".png")):
            # Extract workflow from the metadata of the file
            new_workflow_data = extract_workflow_from_metadata(path)
            if not new_workflow_data:
                error_message = f"No workflow found in the metadata of the file {path}."
                raise Exception(error_message)

            # Check if a workflow with the same data already exists
            workflow_filename = check_workflow_file_exists(new_workflow_data, workflows_folder)

            # Get target file name and path if workflow does not exist
            if not workflow_filename:
                workflow_filename = os.path.basename(path)
                workflow_filename = os.path.splitext(workflow_filename)[0] + ".json"
                workflow_filename, workflow_path = get_filepath(workflow_filename, workflows_folder)
                try:
                    # Save the file to the workflow folder
                    with open(workflow_path, "w", encoding="utf-8") as file:
                        json.dump(new_workflow_data, file, indent=2, ensure_ascii=False)
                    self.report({'INFO'}, f"Workflow saved to: {workflow_path}")
                    return workflow_filename
                except Exception as e:
                    error_message = f"Failed to save workflow from {path}: {e}"
                    raise Exception(error_message)
            else:
                self.report({'INFO'}, f"Workflow already exists: {workflow_filename}")
                return workflow_filename

        else:
            error_message = f"Selected file extension is not supported: {path}"
            raise Exception(error_message)


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportWorkflow)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportWorkflow)

"""Operator to import a workflow from a file metadata."""
import os
import json

import bpy

from ..utils import get_filepath, show_error_popup


class ComfyBlenderOperatorImportWorkflowFromMetadata(bpy.types.Operator):
    """Operator to import a workflow from a file metadata."""

    bl_idname = "comfy.import_workflow_from_metadata"
    bl_label = "Reload Workflow"
    bl_description = "Import workflow from file metadata"

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    type: bpy.props.StringProperty(name="Type")

    def execute(self, context):
        """Execute the operator."""

        if self.type == "image":
            # Extract metadata from the image file
            with open(self.filepath, "rb") as file:
                data = file.read()
            for chunk_type, chunk_data in self.chunk_iter(data):
                if chunk_type == b'tEXt':
                    key, value = chunk_data.decode("iso-8859-1").split("\0")
                    metadata = {key: json.loads(value)}

            # Get workflows folder and workflow filename
            addon_prefs = context.preferences.addons["comfyui_blender"].preferences
            workflows_folder = str(addon_prefs.workflows_folder)
            workflow_filename = os.path.basename(self.filepath)
            workflow_filename = os.path.splitext(workflow_filename)[0] + ".json"

            # Create the workflows folder if it doesn't exist
            os.makedirs(workflows_folder, exist_ok=True)

            # Get target file name and path
            workflow_filename, workflow_path = get_filepath(workflow_filename, workflows_folder)

            # Write metadata to JSON file
            if metadata["prompt"]:
                # Add a flag to keep current values when reloading the workflow
                # Instead of using the default values
                metadata["prompt"]["comfyui_blender"] = {}
                metadata["prompt"]["comfyui_blender"]["keep_values"] = True
                try:
                    with open(workflow_path, "w", encoding="utf-8") as file:
                        json.dump(metadata["prompt"], file, indent=2, ensure_ascii=False)
                    self.report({'INFO'}, f"Workflow saved to: {workflow_path}")

                except Exception as e:
                    error_message = f"Failed to save workflow: {e}"
                    show_error_popup(error_message)
                    return {'CANCELLED'}
            
            # Set current workflow to load workflow
            addon_prefs.workflow = workflow_filename

        else:
            error_message = "File type is not supported."
            show_error_popup(error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def chunk_iter(self, data):
        """Iterate over PNG data chunks to extract metadata. This function was borrowed from:
        https://blender.stackexchange.com/questions/35504/read-image-metadata-from-python"""

        total_length = len(data)
        end = 4

        while(end + 8 < total_length):     
            length = int.from_bytes(data[end + 4: end + 8], 'big')
            begin_chunk_type = end + 8
            begin_chunk_data = begin_chunk_type + 4
            end = begin_chunk_data + length
            yield (data[begin_chunk_type: begin_chunk_data], data[begin_chunk_data: end])
 
def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportWorkflowFromMetadata)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportWorkflowFromMetadata)

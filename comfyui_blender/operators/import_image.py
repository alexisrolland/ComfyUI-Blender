"""Operator to import an image."""
import os
import shutil

import bpy

from ..utils import get_filepath, show_error_popup


class ComfyBlenderOperatorImportImage(bpy.types.Operator):
    """Operator to import an image."""

    bl_idname = "comfy.import_image"
    bl_label = "Import Image"
    bl_description = "Import an image"

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(name="File Filter", default="*.jpeg;*.jpg;*.png;*.webp")
    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

        if self.filepath.lower().endswith((".jpeg", ".jpg", ".png", ".webp")):
            addon_prefs = context.preferences.addons["comfyui_blender"].preferences
            inputs_folder = str(addon_prefs.inputs_folder)
            input_filename = os.path.basename(self.filepath)

            # Create the inputs folder if it doesn't exist
            os.makedirs(inputs_folder, exist_ok=True)

            # Get target path
            input_filename, input_filepath = get_filepath(input_filename, inputs_folder)

            try:
                # Copy the file to the inputs folder
                shutil.copy(self.filepath, input_filepath)
                self.report({'INFO'}, f"Input copied to: {input_filepath}")

            except Exception as e:
                error_message = f"Failed to copy input file: {e}"
                show_error_popup(error_message)
                return {'CANCELLED'}

            # Load image in the data block
            bpy.data.images.load(input_filepath, check_existing=True)

            # Delete the previous input file from Blender's data if it exists
            current_workflow = context.scene.current_workflow
            previous_input_filepath = getattr(current_workflow, self.workflow_property)
            previous_input_filename = os.path.basename(previous_input_filepath)
            if bpy.data.images.get(previous_input_filename):
                image = bpy.data.images.get(previous_input_filename)
                bpy.data.images.remove(image)

            # Update the workflow property with the new input filepath
            current_workflow[self.workflow_property] = input_filepath

        else:
            error_message = "Selected file is not a *.jpeg;*.jpg;*.png;*.webp."
            show_error_popup(error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector for importing a workflow."""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportImage)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportImage)

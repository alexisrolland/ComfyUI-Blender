"""Operator to import an input image."""
import os
import shutil

import bpy

from ..utils import show_error_popup, upload_file


class ComfyBlenderOperatorImportInputImage(bpy.types.Operator):
    """Operator to import an input image."""

    bl_idname = "comfy.import_input_image"
    bl_label = "Import Input Image"
    bl_description = "Import an input image"

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(name="File Filter", default="*.jpeg;*.jpg;*.png;*.webp")
    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

        if self.filepath.lower().endswith((".jpeg", ".jpg", ".png", ".webp")):
            # Upload file on ComfyUI server
            response = upload_file(self.filepath, type="image")
            if response.status_code != 200:
                error_message = f"Failed to upload file: {response.status_code} - {response.text}"
                show_error_popup(error_message)
                return {'CANCELLED'}

            # Delete the previous input file from Blender's data if it exists
            current_workflow = context.scene.current_workflow
            previous_input = getattr(current_workflow, self.workflow_property)
            if bpy.data.images.get(previous_input):
                image = bpy.data.images.get(previous_input)
                bpy.data.images.remove(image)

            # Build input file paths
            addon_prefs = context.preferences.addons["comfyui_blender"].preferences
            inputs_folder = str(addon_prefs.inputs_folder)
            input_subfolder = response.json()["subfolder"]
            input_filename = response.json()["name"]
            input_fullpath = os.path.join(inputs_folder, input_subfolder, input_filename)

            # Create the input subfolder if it doesn't exist
            os.makedirs(os.path.join(inputs_folder, input_subfolder), exist_ok=True)

            try:
                # Copy the file to the inputs folder
                shutil.copy(self.filepath, input_fullpath)
                self.report({'INFO'}, f"Input copied to: {input_fullpath}")

            except Exception as e:
                error_message = f"Failed to copy input file: {e}"
                show_error_popup(error_message)
                return {'CANCELLED'}

            # Load image in the data block
            image = bpy.data.images.load(input_fullpath, check_existing=True)

            # Update the workflow property with the input file path as defined on the ComfyUI server
            current_workflow[self.workflow_property] = os.path.join(input_subfolder, input_filename)

        else:
            error_message = "Selected file is not a *.jpeg;*.jpg;*.png;*.webp."
            show_error_popup(error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector."""

        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        outputs_folder = addon_prefs.outputs_folder
        
        # Set the filepath to the folder and add a trailing slash/backslash
        if not outputs_folder.endswith(os.sep):
            outputs_folder += os.sep
        self.filepath = outputs_folder

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportInputImage)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportInputImage)

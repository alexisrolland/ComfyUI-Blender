"""Operator to send an image or text object to a workflow input."""
import logging
import os
import shutil

import bpy

from ..workflow import get_current_workflow_inputs
from ..utils import (
    get_filepath,
    get_inputs_folder,
    get_temp_folder,
    upload_file
)

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorSendToInput(bpy.types.Operator):
    """Operator to send the current image to a workflow input."""

    bl_idname = "comfy.send_to_input"
    bl_label = "Send to Input"
    bl_description = "Send the image to the target input of the current workflow."

    name: bpy.props.StringProperty(name="Name")
    type: bpy.props.StringProperty(name="Type")
    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

        # Manage image input
        if self.type == "image":
            temp_filename = "blender_input.png"

            # Get image
            image = bpy.data.images.get(self.name)
            if not image:
                error_message = f"Image not found in Blender data"
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            # Check the current workflow contains a valid input
            if not self.workflow_property:
                error_message = "No image or mask input in the selected workflow. Make sure to add a node 'Blender Input Load Image' or 'Blender Input Load Mask' in the workflow."
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            # Build temp file paths
            temp_folder = get_temp_folder()
            temp_filepath = os.path.join(temp_folder, temp_filename)

            # Duplicate the image to ensure it has an alpha channel
            new_image = bpy.data.images.new(name=temp_filename, width=image.size[0], height=image.size[1], alpha=True)
            new_image.pixels = image.pixels[:]
            new_image.file_format = "PNG"
            new_image.filepath_raw = temp_filepath
            new_image.save()
            bpy.data.images.remove(new_image)

            # Upload file on ComfyUI server
            try:
                response = upload_file(temp_filepath, type="image")
            except Exception as e:
                addon_prefs = context.preferences.addons["comfyui_blender"].preferences
                error_message = f"Failed to upload file to ComfyUI server: {addon_prefs.server_address}. {e}"
                log.exception(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            if response.status_code != 200:
                error_message = f"Failed to upload file: {response.status_code} - {response.text}"
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            # Delete the previous input image from Blender's data
            # Only if the image is not used in any of the workflow inputs
            current_workflow = context.scene.current_workflow
            previous_image = getattr(current_workflow, self.workflow_property)
            if previous_image:
                possible_inputs = get_current_workflow_inputs(self, context, ("BlenderInputLoadImage", "BlenderInputLoadMask"))
                is_used = False  # Flag to check if the image is used in any other input
                for input in possible_inputs:
                    if input[0] != self.workflow_property:
                        if getattr(current_workflow, input[0]) == previous_image:
                            is_used = True
                            break
                if not is_used:
                    bpy.data.images.remove(previous_image)

            # Build input file paths
            inputs_folder = get_inputs_folder()
            input_subfolder = response.json()["subfolder"]
            input_filename = response.json()["name"]
            input_filepath = os.path.join(inputs_folder, input_subfolder, input_filename)

            # Create the input subfolder if it doesn't exist
            os.makedirs(os.path.join(inputs_folder, input_subfolder), exist_ok=True)

            try:
                # Copy the file to the inputs folder
                shutil.copy(temp_filepath, input_filepath)
                self.report({'INFO'}, f"Input file copied to: {input_filepath}")
            except shutil.SameFileError as e:
                self.report({'INFO'}, f"Input file is already in the inputs folder: {input_filepath}")
            except Exception as e:
                error_message = f"Failed to copy input file: {e}"
                log.exception(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            # Load image in the data block
            image = bpy.data.images.load(input_filepath, check_existing=True)

            # Update the workflow property with the image from the data block
            setattr(current_workflow, self.workflow_property, image)

            # Remove temporary files
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

        # Manage text input
        elif self.type == "text":
            temp_filename = "blender_input.txt"

            # Get text object
            text = bpy.data.texts.get(self.name)
            if not text:
                error_message = f"Text object not found in Blender data"
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            # Check the current workflow contains a valid input
            if not self.workflow_property:
                error_message = "No string multiline input in the selected workflow. Make sure to add a node 'Blender Input Input Multiline' in the workflow."
                log.error(error_message)
                bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
                return {'CANCELLED'}

            # Delete the previous input text from Blender's data
            # Only if the text object is not used in any of the workflow inputs
            current_workflow = context.scene.current_workflow
            previous_text = getattr(current_workflow, self.workflow_property)
            if previous_text:
                possible_inputs = get_current_workflow_inputs(self, context, ("BlenderInputStringMultiline"))
                is_used = False  # Flag to check if the image is used in any other input
                for input in possible_inputs:
                    if input[0] != self.workflow_property:
                        if getattr(current_workflow, input[0]) == previous_text:
                            is_used = True
                            break
                if not is_used:
                    bpy.data.texts.remove(previous_text)

            # Build input file paths
            inputs_folder = get_inputs_folder()
            input_filename, input_filepath = get_filepath(temp_filename, inputs_folder)
            with open(input_filepath, "w") as file:
                file.write(text.as_string())

            # Load text object in the data block
            text = bpy.data.texts.load(input_filepath)

            # Update the workflow property with the text object from the data block
            setattr(current_workflow, self.workflow_property, text)
        return {'FINISHED'}


def register():
    """Register the operator."""

    # Register scene properties for send to input combobox in paint panel
    # Use a lambda function to pass arguments to get_current_workflow_inputs
    bpy.types.Scene.comfyui_target_input = bpy.props.EnumProperty(
        name="Target Input",
        description="Target input to send to",
        items=lambda self, context: get_current_workflow_inputs(self, context, ("BlenderInputLoadImage", "BlenderInputLoadMask"))
    )

    bpy.utils.register_class(ComfyBlenderOperatorSendToInput)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorSendToInput)

    # Check if attributes exist before deleting them
    if hasattr(bpy.types.Scene, "comfyui_target_input"):
        del bpy.types.Scene.comfyui_target_input

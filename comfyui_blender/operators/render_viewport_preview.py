"""Operator to render viewport preview."""
import logging
import os
import shutil

import bpy

from ..utils import get_inputs_folder, get_temp_folder, upload_file

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorRenderViewportPreview(bpy.types.Operator):
    """Operator to render viewport preview."""

    bl_idname = "comfy.render_viewport_preview"
    bl_label = "Render Viewport Preview"
    bl_description = "Render the viewport preview and upload it to the ComfyUI server."

    workflow_property: bpy.props.StringProperty(name="Workflow Property")
    temp_filename = "blender_viewport_preview"

    def reset_scene(self, context, **kwargs):
        """Reset the scene to its initial state."""

        # Restore original render settings
        scene = context.scene
        scene.render.filepath = kwargs["original_filepath"]
        scene.render.image_settings.file_format = kwargs["original_file_format"]
        scene.render.image_settings.color_mode = kwargs["original_color_mode"]

        # Remove temporary files
        if os.path.exists(kwargs["temp_filepath"]):
            os.remove(kwargs["temp_filepath"])

    def execute(self, context):
        """Execute the operator."""

        scene = context.scene

        # Check if we're in a 3D viewport
        area = None
        for window in context.window_manager.windows:
            for area_item in window.screen.areas:
                if area_item.type == 'VIEW_3D':
                    area = area_item
                    break
            if area:
                break

        if not area:
            error_message = "No 3D viewport found"
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Build temp file paths
        temp_folder = get_temp_folder()
        temp_filename = f"{self.temp_filename}.png"
        temp_filepath = os.path.join(temp_folder, temp_filename)

        # Initialize scene reset settings
        reset_params = {}
        reset_params["temp_filepath"] = temp_filepath
        reset_params["original_filepath"] = scene.render.filepath
        reset_params["original_file_format"] = scene.render.image_settings.file_format
        reset_params["original_color_mode"] = scene.render.image_settings.color_mode

        # Set up the scene for rendering
        scene.render.filepath = temp_filepath
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"

        # Override context to render from the 3D viewport
        override = context.copy()
        override['area'] = area
        override['region'] = area.regions[-1]

        # Render the viewport using OpenGL
        try:
            with context.temp_override(**override):
                bpy.ops.render.opengl(write_still=True)
        except Exception as e:
            # Reset the scene to initial state
            self.reset_scene(context, **reset_params)
            error_message = f"Failed to render viewport: {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Upload file on ComfyUI server
        try:
            response = upload_file(temp_filepath, type="image")
        except Exception as e:
            # Reset the scene to initial state
            self.reset_scene(context, **reset_params)
            addon_prefs = context.preferences.addons["comfyui_blender"].preferences
            error_message = f"Failed to upload file to ComfyUI server: {addon_prefs.server_address}. {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        if response.status_code != 200:
            # Reset the scene to initial state
            self.reset_scene(context, **reset_params)
            error_message = f"Failed to upload file: {response.status_code} - {response.text}"
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Delete the previous input image from Blender's data
        current_workflow = scene.current_workflow
        previous_image = getattr(current_workflow, self.workflow_property)
        if previous_image:
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
            # Reset the scene to initial state
            self.reset_scene(context, **reset_params)
            error_message = f"Failed to copy input file: {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Load image in the data block
        image = bpy.data.images.load(input_filepath, check_existing=True)

        # Update the workflow property with the image from the data block
        setattr(current_workflow, self.workflow_property, image)

        # Reset the scene to initial state
        self.reset_scene(context, **reset_params)
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRenderViewportPreview)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRenderViewportPreview)

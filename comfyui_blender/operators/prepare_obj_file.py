"""Operator to prepare an OBJ file to import it on the ComfyUI server."""
import logging
import os
import shutil

import bpy

from ..utils import upload_file

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorPrepare3DModel(bpy.types.Operator):
    """Operator to prepare an OBJ file to import it on the ComfyUI server."""

    bl_idname = "comfy.prepare_obj_file"
    bl_label = "Prepare OBJ file"
    bl_description = "Prepare an OBJ file to import it on the ComfyUI server"

    workflow_property: bpy.props.StringProperty(name="Workflow Property")
    temp_filename = "blender_3d_model.obj"

    def execute(self, context):
        """Execute the operator."""

        # Check if a mesh object is selected
        selected_meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]
        if not selected_meshes:
            error_message = f"Select at least one mesh object."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Build temp file paths
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        temp_folder = str(addon_prefs.temp_folder)
        temp_filepath = os.path.join(temp_folder, self.temp_filename)

        # Export selected meshes
        bpy.ops.wm.obj_export(filepath=temp_filepath, export_selected_objects=True, export_materials=False)

        # Upload file on ComfyUI server
        try:
            response = upload_file(temp_filepath, type="3d")
        except Exception as e:
            error_message = f"Failed to upload file to ComfyUI server: {addon_prefs.server_address}. {e}"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        if response.status_code != 200:
            error_message = f"Failed to upload file: {response.status_code} - {response.text}"
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Build input file paths
        inputs_folder = str(addon_prefs.inputs_folder)
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

        # Update the workflow property with the input file path as defined on the ComfyUI server
        # Do not use os.path.join because the node on ComfyUI server normalizes the path in Linux style
        current_workflow = context.scene.current_workflow
        current_workflow[self.workflow_property] = f"{input_subfolder}/{input_filename}"

        # Remove temporary files
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorPrepare3DModel)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorPrepare3DModel)

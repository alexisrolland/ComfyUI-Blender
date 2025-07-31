"""Operator to prepare a 3D model file to import it on ComfyUI server."""
import os

import bpy

from ..utils import get_filepath, show_error_popup


class ComfyBlenderOperatorPrepare3DModel(bpy.types.Operator):
    """Operator to prepare a 3D model file to import it on ComfyUI server."""

    bl_idname = "comfy.prepare_3d_model"
    bl_label = "Prepare 3D Model"
    bl_description = "Prepare a 3D model file to import it on ComfyUI server"

    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

        # Check if any mesh object is selected
        selected_meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]
        if not selected_meshes:
            error_message = f"Select at least one mesh object."
            show_error_popup(error_message)
            return {'CANCELLED'}

        # Delete the previous input file
        current_workflow = context.scene.current_workflow
        previous_input_filepath = getattr(current_workflow, self.workflow_property)
        if os.path.exists(previous_input_filepath):
            os.remove(previous_input_filepath)

        # Get path to inputs folder
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        inputs_folder = str(addon_prefs.inputs_folder)
        os.makedirs(inputs_folder, exist_ok=True)
        file_name, filepath = get_filepath("3d_model.obj", inputs_folder)

        # Export selected meshes
        bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True, export_materials=False)

        # Update the workflow property with the new input filepath
        current_workflow[self.workflow_property] = filepath
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorPrepare3DModel)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorPrepare3DModel)

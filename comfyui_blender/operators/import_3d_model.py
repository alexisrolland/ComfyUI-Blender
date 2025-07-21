"""Operator to import a 3D model into the scene."""
import os
import shutil

import bpy

from ..utils import get_filepath, show_error_popup


class ComfyBlenderOperatorImport3DModel(bpy.types.Operator):
    """Operator to import a 3D model into the scene."""

    bl_idname = "comfy.import_3d_model"
    bl_label = "Import 3D Model"
    bl_description = "Import a 3D model into the scene"

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")

    def execute(self, context):
        """Execute the operator."""

        # Get file extension to determine import method
        _, ext = os.path.splitext(self.filepath)
        ext = ext.lower()
 
        if ext == ".obj":
            bpy.ops.wm.obj_import(filepath=self.filepath)
        elif ext == ".ply":
            bpy.ops.wm.ply_import(filepath=self.filepath)
        elif ext == ".stl":
            bpy.ops.wm.stl_import(filepath=self.filepath)
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=self.filepath)
        elif ext in ".dae":
            bpy.ops.wm.collada_import(filepath=self.filepath)
        else:
            error_message = f"Unsupported file format: {ext}"
            show_error_popup(error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector for importing a workflow."""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImport3DModel)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImport3DModel)

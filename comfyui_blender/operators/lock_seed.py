"""Operator to lock a seed value."""
import bpy

from ..utils import get_filepath


class ComfyBlenderOperatorLockSeed(bpy.types.Operator):
    """Operator to lock a seed value."""

    bl_idname = "comfy.lock_seed"
    bl_label = "Lock Seed"
    bl_description = "Lock a seed value."

    def execute(self, context):
        """Execute the operator."""
        
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorLockSeed)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorLockSeed)

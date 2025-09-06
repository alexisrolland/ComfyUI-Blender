"""Operator to disconnect from the ComfyUI server."""
import logging

import bpy

from ..connection import disconnect

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorDisconnectFromServer(bpy.types.Operator):
    """Operator to disconnect from the ComfyUI server."""

    bl_idname = "comfy.disconnect_from_server"
    bl_label = "Disconnect from Server"
    bl_description = "Disconnect from the ComfyUI server."

    def execute(self, context):
        """Execute the operator."""

        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        if addon_prefs.connection_status:
            self.report({'INFO'}, "Disconnecting from server...")
            disconnect()
        else:
            self.report({'INFO'}, "Already disconnected from server.")
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDisconnectFromServer)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDisconnectFromServer)

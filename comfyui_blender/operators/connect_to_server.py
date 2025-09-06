"""Operator to connect to the ComfyUI server."""
import logging
import threading

import bpy

from ..connection import connect, listen, WS_LISTENER_THREAD

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorConnectToServer(bpy.types.Operator):
    """Operator to connect to the ComfyUI server."""

    bl_idname = "comfy.connect_to_server"
    bl_label = "Connect to Server"
    bl_description = "Connect to the ComfyUI server."

    def execute(self, context):
        """Execute the operator."""

        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        if not addon_prefs.connection_status:
            self.report({'INFO'}, "Connecting to server...")
            connect()
        else:
            self.report({'INFO'}, "Already connected to server.")
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorConnectToServer)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorConnectToServer)

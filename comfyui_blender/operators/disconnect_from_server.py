"""Operator to disconnect from the ComfyUI server."""
import logging

import bpy

from ..connection import disconnect
from ..connection_krita import disconnect as disconnect_krita

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorDisconnectFromServer(bpy.types.Operator):
    """Operator to disconnect from the ComfyUI server."""

    bl_idname = "comfy.disconnect_from_server"
    bl_label = "Disconnect from Server"
    bl_description = "Disconnect from the ComfyUI server."

    client_id: bpy.props.StringProperty(
        name="Client ID",
        description="Custom client ID to pass to the connection menu",
        default=""
    )

    def execute(self, context):
        """Execute the operator."""

        if not self.client_id:
            error_message = "Client Id is required to disconnect from the server."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Primary connection for Blender
        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        if self.client_id == addon_prefs.client_id:
            if addon_prefs.connection_status:
                self.report({'INFO'}, "Disconnecting from server...")
                disconnect()
            else:
                self.report({'INFO'}, "Already disconnected from server.")
        
        # Secondary connection for Krita AI Diffusion
        elif self.client_id == addon_prefs.krita_client_id:
            if addon_prefs.krita_connection_status:
                self.report({'INFO'}, "Disconnecting from server...")
                disconnect_krita()
            else:
                self.report({'INFO'}, "Already disconnected from server.")
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDisconnectFromServer)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDisconnectFromServer)

"""Operator to connect to the ComfyUI server."""
import logging

import bpy

from ..connection import connect
from ..connection_krita import connect as connect_krita

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorConnectToServer(bpy.types.Operator):
    """Operator to connect to the ComfyUI server."""

    bl_idname = "comfy.connect_to_server"
    bl_label = "Connect to Server"
    bl_description = "Connect to the ComfyUI server."

    client_id: bpy.props.StringProperty(
        name="Client ID",
        description="Custom client ID to pass to the connection menu",
        default=""
    )

    def execute(self, context):
        """Execute the operator."""

        if not self.client_id:
            error_message = "Client Id is required to connect to the server."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Primary connection for Blender
        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        if self.client_id == addon_prefs.client_id:
            if not addon_prefs.connection_status:
                self.report({'INFO'}, "Connecting to server...")
                connect()
            else:
                self.report({'INFO'}, "Already connected to server.")
        
        # Secondary connection for Krita AI Diffusion
        elif self.client_id == addon_prefs.krita_client_id:
            if not addon_prefs.krita_connection_status:
                self.report({'INFO'}, "Connecting to server...")
                connect_krita()
            else:
                self.report({'INFO'}, "Already connected to server.")

        else:
            error_message = f"Client Id '{self.client_id}' does not match any configured client Id."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorConnectToServer)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorConnectToServer)

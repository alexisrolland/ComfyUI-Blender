import bpy
from .utils import stop_websocket_listener

class COMFY_OT_DisconnectFromServer(bpy.types.Operator):
    """Operator to connect to the ComfyUI server."""
    bl_idname = "comfy.disconnect_from_server"
    bl_label = "Disconnect From Server"
    bl_description = "Terminate the WebSocket connection from the ComfyUI server"

    def execute(self, context):
        stop_websocket_listener(operator=self)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(COMFY_OT_DisconnectFromServer)

def unregister():
    bpy.utils.unregister_class(COMFY_OT_DisconnectFromServer)
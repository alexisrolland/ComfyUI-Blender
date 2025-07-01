import bpy
from .utils import start_websocket_listener

class COMFY_OT_ConnectToServer(bpy.types.Operator):
    """Operator to connect to the ComfyUI server."""
    bl_idname = "comfy.connect_to_server"
    bl_label = "Connect To Server"
    bl_description = "Establish a WebSocket connection to the ComfyUI server"

    def execute(self, context):
        # Get the server address from addon preferences
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        client_id = context.scene.client_id
        server_address = addon_prefs.server_address
        
        # Construct WebSocket server address
        server_address = server_address.rstrip("/")
        server_address = server_address + f"/ws?clientId={client_id}"
        if "https://" in server_address:
            server_address = server_address.replace("https://", "wss://")
        elif "http://" in server_address:
            server_address = server_address.replace("http://", "ws://")

        start_websocket_listener(server_address, operator=self)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(COMFY_OT_ConnectToServer)

def unregister():
    bpy.utils.unregister_class(COMFY_OT_ConnectToServer)
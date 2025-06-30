import bpy
import websocket

class COMFY_PT_OutputPanel(bpy.types.Panel):
    bl_label = "Outputs"
    bl_idname = "COMFY_PT_OutputPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw(self, context):
        # Get the server address from addon preferences
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        server_address = addon_prefs.server_address.replace("http://", "").replace("https://", "")
        client_id = context.scene.client_id

        # Establish websocket connection to the ComfyUI server
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

        # Listen for messages from the server
        prompt_id = context.scene.prompt_id
        #while True:
        #    out = ws.recv()
        #    print(out)
        #    if isinstance(out, str):
        #        message = json.loads(out)
        #        if message['type'] == 'executing':
        #            data = message['data']
        #            if data['node'] is None and data['prompt_id'] == prompt_id:
        #                break #Execution is done
        #    else:
                # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
                # bytesIO = BytesIO(out[8:])
                # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
        #        continue #previews are binary data

        layout = self.layout

def register():
    bpy.utils.register_class(COMFY_PT_OutputPanel)

def unregister():
    bpy.utils.unregister_class(COMFY_PT_OutputPanel)
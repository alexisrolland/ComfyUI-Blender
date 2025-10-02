"""Context menu to provide connection options."""
import bpy


class ComfyBlenderConnectionMenu(bpy.types.Menu):
    """Context menu to provide connection options."""
    
    bl_label = ""  # Hide label
    bl_idname = "COMFY_MT_connection_menu"
    
    def draw(self, context):
        layout = self.layout

        # Get the client_id passed from show_connection_menu
        client_id = context.scene.get("comfyui_client_id", "")

        # Primary connection for Blender
        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        if client_id == addon_prefs.client_id:
            # Connect
            row = layout.row()
            row.enabled = addon_prefs.connection_status == False
            connect = row.operator("comfy.connect_to_server", text="Connect", icon="INTERNET")
            connect.client_id = client_id

            # Disconnect
            row = layout.row()
            row.enabled = addon_prefs.connection_status == True
            disconnect = row.operator("comfy.disconnect_from_server", text="Disconnect", icon="INTERNET_OFFLINE")
            disconnect.client_id = client_id

        # Secondary connection for Krita AI Diffusion
        elif client_id == addon_prefs.krita_client_id:
            # Connect
            row = layout.row()
            row.enabled = addon_prefs.krita_connection_status == False
            connect = row.operator("comfy.connect_to_server", text="Connect", icon="INTERNET")
            connect.client_id = client_id

            # Disconnect
            row = layout.row()
            row.enabled = addon_prefs.krita_connection_status == True
            disconnect = row.operator("comfy.disconnect_from_server", text="Disconnect", icon="INTERNET_OFFLINE")
            disconnect.client_id = client_id


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderConnectionMenu)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderConnectionMenu)
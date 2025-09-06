"""Context menu to provide connection options."""
import bpy


class ComfyBlenderConnectionMenu(bpy.types.Menu):
    """Context menu to provide connection options."""
    
    bl_label = ""  # Hide label
    bl_idname = "COMFY_MT_connection_menu"
    
    def draw(self, context):
        layout = self.layout

        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences

        # Connect
        row = layout.row()
        row.enabled = addon_prefs.connection_status == False
        row.operator("comfy.connect_to_server", text="Connect", icon="INTERNET")

        # Disconnect
        row = layout.row()
        row.enabled = addon_prefs.connection_status == True
        row.operator("comfy.disconnect_from_server", text="Disconnect", icon="INTERNET_OFFLINE")


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderConnectionMenu)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderConnectionMenu)
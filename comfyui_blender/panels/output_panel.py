"""Panel to display generated outputs."""
import bpy


class ComfyBlenderPanelOutput(bpy.types.Panel):
    """Panel to display generated outputs."""

    bl_label = "Outputs"
    bl_idname = "COMFY_PT_Output"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw(self, context):
        """Draw the panel."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        queue = addon_prefs.queue
        connection_status = addon_prefs.connection_status

        layout = self.layout
        row = layout.row()
        if connection_status:
            row.label(text=f"Queue: {queue}", icon="RADIOBUT_ON")
        else:
            row.label(text=f"Queue: {queue}", icon="RADIOBUT_OFF")

        layout.operator("comfy.open_file_browser", text="Open Outputs Folder")

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelOutput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelOutput)

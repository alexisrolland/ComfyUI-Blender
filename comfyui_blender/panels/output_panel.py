import bpy

class COMFY_PT_OutputPanel(bpy.types.Panel):
    bl_label = "Outputs"
    bl_idname = "COMFY_PT_OutputPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw(self, context):
        layout = self.layout

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        connection_status = addon_prefs.connection_status
        row = layout.row()
        row.prop(context.scene, "queue", emboss=False)
        if connection_status:
           row.label(icon="RADIOBUT_ON")
        else:
           row.label(icon="RADIOBUT_OFF")


def register():
    bpy.utils.register_class(COMFY_PT_OutputPanel)

def unregister():
    bpy.utils.unregister_class(COMFY_PT_OutputPanel)
import bpy

class COMFY_PT_ComfyUIPanel(bpy.types.Panel):
    bl_label = "ComfyUI"
    bl_idname = "COMFY_PT_ComfyUIPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        # Buttons to import workflow and show preferences
        row.operator("comfy.import_workflow", text="Import Workflow")
        row.operator("preferences.addon_show", icon="PREFERENCES").module = "comfyui_blender"

        # Dropdown list of workflows
        layout.prop(context.scene, "workflow")

def register():
    bpy.utils.register_class(COMFY_PT_ComfyUIPanel)

def unregister():
    bpy.utils.unregister_class(COMFY_PT_ComfyUIPanel)
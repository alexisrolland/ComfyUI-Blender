import bpy

class COMFY_OT_SelectOutputFolder(bpy.types.Operator):
    """Operator to select a folder for outputs."""
    bl_idname = "comfy.select_output_folder"
    bl_label = "Select Output Folder"
    bl_description = "Select a folder where outptus are stored"

    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        addon_prefs.output_folder = self.directory
        self.report({'INFO'}, f"Output folder set to: {self.directory}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(COMFY_OT_SelectOutputFolder)

def unregister():
    bpy.utils.unregister_class(COMFY_OT_SelectOutputFolder)
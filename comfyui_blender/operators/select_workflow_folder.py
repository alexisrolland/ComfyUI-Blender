import bpy

class COMFY_OT_SelectWorkflowFolder(bpy.types.Operator):
    """Operator to select a folder for workflows."""
    bl_idname = "comfy.select_workflow_folder"
    bl_label = "Select Workflow Folder"
    bl_description = "Select a folder where workflows are stored"

    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        addon_prefs.workflow_folder = self.directory
        self.report({'INFO'}, f"Workflow folder set to: {self.directory}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(COMFY_OT_SelectWorkflowFolder)

def unregister():
    bpy.utils.unregister_class(COMFY_OT_SelectWorkflowFolder)
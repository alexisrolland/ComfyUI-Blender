"""Operator to select a folder for outputs."""
import bpy


class ComfyBlenderOperatorSelectOutputFolder(bpy.types.Operator):
    """Operator to select a folder for outputs."""

    bl_idname = "comfy.select_outputs_folder"
    bl_label = "Select Output Folder"
    bl_description = "Select a folder where outptus are stored"

    directory: bpy.props.StringProperty(name="Directory", subtype="DIR_PATH")

    def execute(self, context):
        """Execute the operator."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        addon_prefs.outputs_folder = self.directory
        self.report({'INFO'}, f"Outputs folder set to: {self.directory}")
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector for selecting a folder."""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorSelectOutputFolder)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorSelectOutputFolder)

"""Operator to select a folder."""
import bpy
from bpy.props import StringProperty


class ComfyBlenderOperatorSelectFolder(bpy.types.Operator):
    """Operator to select a folder."""

    bl_idname = "comfy.select_folder"
    bl_label = "Select Folder"
    bl_description = "Select a folder"

    directory: StringProperty(name="Directory", subtype="DIR_PATH")
    target_property: StringProperty(name="Target Property")

    def execute(self, context):
        """Execute the operator."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        if self.target_property == "base_folder":
            addon_prefs.base_folder = self.directory

        elif self.target_property == "workflows_folder":
            addon_prefs.workflows_folder = self.directory

        elif self.target_property == "inputs_folder":
            addon_prefs.inputs_folder = self.directory

        elif self.target_property == "outputs_folder":
            addon_prefs.outputs_folder = self.directory

        self.report({'INFO'}, f"Folder set to: {self.directory}")
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector for selecting a folder."""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorSelectFolder)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorSelectFolder)

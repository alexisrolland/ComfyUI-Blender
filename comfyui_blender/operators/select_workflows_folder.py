"""Operator to select a folder for workflows."""
import bpy


class ComfyBlenderOperatorSelectWorkflowFolder(bpy.types.Operator):
    """Operator to select a folder for workflows."""

    bl_idname = "comfy.select_workflows_folder"
    bl_label = "Select Workflow Folder"
    bl_description = "Select a folder where workflows are stored"

    directory: bpy.props.StringProperty(name="Directory", subtype="DIR_PATH")

    def execute(self, context):
        """Execute the operator."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        addon_prefs.workflows_folder = self.directory
        self.report({'INFO'}, f"Workflows folder set to: {self.directory}")
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector for selecting a folder."""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorSelectWorkflowFolder)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorSelectWorkflowFolder)

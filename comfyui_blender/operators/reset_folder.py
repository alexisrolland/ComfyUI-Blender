"""Operator to reset a folder."""
import bpy
import os
from bpy.props import StringProperty


class ComfyBlenderOperatorResetFolder(bpy.types.Operator):
    """Operator to reset a folder."""

    bl_idname = "comfy.reset_folder"
    bl_label = "Reset Folder"
    bl_description = "Reset the folder."

    target_property: StringProperty(name="Target Property")

    def execute(self, context):
        """Execute the operator."""

        # Build path to the addon's data folder
        # Gets package name 'comfyui_blender' instead of 'comfyui_blender.operators'
        parent_package = __package__.split(".")[0]
        base_path = os.path.dirname(bpy.utils.resource_path("USER"))
        base_path = os.path.join(base_path, "data", parent_package)

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        if self.target_property == "base_folder":
            addon_prefs.base_folder = base_path
            os.makedirs(addon_prefs.base_folder, exist_ok=True)

        elif self.target_property == "inputs_folder":
            addon_prefs.inputs_folder = os.path.join(base_path, "inputs")
            os.makedirs(addon_prefs.inputs_folder, exist_ok=True)

        elif self.target_property == "outputs_folder":
            addon_prefs.outputs_folder = os.path.join(base_path, "outputs")
            os.makedirs(addon_prefs.outputs_folder, exist_ok=True)

        elif self.target_property == "workflows_folder":
            addon_prefs.workflows_folder = os.path.join(base_path, "workflows")
            os.makedirs(addon_prefs.workflows_folder, exist_ok=True)

        # Save user preferences to retain the folder selection when restarting Blender
        bpy.ops.wm.save_userpref()

        self.report({'INFO'}, f"Folder set to: {addon_prefs.base_folder}")
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorResetFolder)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorResetFolder)

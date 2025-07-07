"""Operator to open Blender's built-in file browser."""
import bpy


class ComfyBlenderOperatorOpenFileBrowser(bpy.types.Operator):
    """Operator to open Blender's built-in file browser."""

    bl_idname = "comfy.open_file_browser"
    bl_label = "Open File Browser"
    bl_description = "Open Blender's built-in file browser"

    def execute(self, context):
        """Execute the operator."""

        # Open area and change it to a file browser
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.25)
        areas = context.screen.areas
        areas[-1].type = "FILE_BROWSER"

        # Set the folder path of the file browser to a specific path
        for space in areas[-1].spaces:
            if space.type == "FILE_BROWSER":
                addon_prefs = context.preferences.addons["comfyui_blender"].preferences
                outputs_folder = addon_prefs.outputs_folder.encode()
                space.params.directory = outputs_folder
        bpy.ops.comfy.set_file_browser_path()
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorOpenFileBrowser)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorOpenFileBrowser)

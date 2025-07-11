"""Operator to open Blender's built-in file browser."""
import bpy


class ComfyBlenderOperatorOpenFileBrowser(bpy.types.Operator):
    """Operator to open Blender's built-in file browser."""

    bl_idname = "comfy.open_file_browser"
    bl_label = "Open File Browser"
    bl_description = "Open Blender's built-in file browser"

    def execute(self, context):
        """Execute the operator."""

        # Split the screen to create a new area
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.25)

        # Get the newly created area (the last one)
        area = context.screen.areas[-1]
        area.type = "FILE_BROWSER"

        # Access the file browser space
        space = area.spaces[0]

        # Set the directory path using a timer to ensure it is initialized
        def set_directory():
            if space.params is not None:
                addon_prefs = context.preferences.addons["comfyui_blender"].preferences
                space.params.directory = addon_prefs.outputs_folder.encode("utf-8")
                return None  # Stop the timer
            return 0.1  # Try again in 0.1 seconds

        # Use a timer to set the directory after initialization
        bpy.app.timers.register(set_directory, first_interval=0.1)
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorOpenFileBrowser)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorOpenFileBrowser)

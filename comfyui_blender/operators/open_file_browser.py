"""Operator to open Blender's file browser."""
import bpy


class ComfyBlenderOperatorOpenFileBrowser(bpy.types.Operator):
    """Operator to open Blender's file browser."""

    bl_idname = "comfy.open_file_browser"
    bl_label = "Open File Browser"
    bl_description = "Open Blender's file browser"

    folder_path: bpy.props.StringProperty(name="Folder Path")

    def execute(self, context):
        """Execute the operator."""

        # Check if there is already a file browser area
        file_browser_area = None
        for area in context.screen.areas:
            if area.type == "FILE_BROWSER":
                file_browser_area = area
                break

        # If no file browser area exists, split the screen to create one
        if file_browser_area is None:
            bpy.ops.screen.area_split(direction="VERTICAL", factor=0.3)

            # Get the newly created area (the last one)
            file_browser_area = context.screen.areas[-1]
            file_browser_area.type = "FILE_BROWSER"

        # Access the file browser space
        space = file_browser_area.spaces[0]

        # Capture the folder path before registering the timer
        # This is necessary to ensure access to the folder path after garbage collection
        folder_path = self.folder_path

        # Set the directory path using a timer to ensure it is initialized
        def set_directory():
            if space.params is not None:
                space.params.directory = folder_path.encode("utf-8")
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

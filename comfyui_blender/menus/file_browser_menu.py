"""Context menu to provide custom actions in the file browser."""
import os

import bpy


def draw_file_browser_menu(self, context):
    """Context menu to provide custom actions in the file browser."""

    layout = self.layout
    layout.separator(type="LINE")
    layout.label(text="ComfyUI")

    # Get selected file
    if hasattr(context, "active_file"):
        directory = context.space_data.params.directory.decode("utf-8")
        filename = context.active_file.name
        filepath = os.path.join(directory, filename)

        # Open image
        if filename.lower().endswith((".jpeg", ".jpg", ".png", ".webp")):
            open_image = layout.operator("comfy.open_image")
            open_image.filepath = filepath
            open_image.invoke_default = False

        # Import workflow
        if filename.lower().endswith((".json", ".png")):
            import_workflow = layout.operator("comfy.import_workflow")
            import_workflow.filepath = filepath
            import_workflow.invoke_default = False

def register():
    """Register the panel."""

    bpy.types.FILEBROWSER_MT_context_menu.append(draw_file_browser_menu)

def unregister():
    """Unregister the panel."""

    bpy.types.FILEBROWSER_MT_context_menu.remove(draw_file_browser_menu)

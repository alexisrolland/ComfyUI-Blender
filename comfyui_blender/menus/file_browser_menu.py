"""Context menu to provide custom actions in the file browser."""
import os

import bpy


def draw_file_browser_menu(self, context):
    """Context menu to provide custom actions in the file browser."""

    layout = self.layout
    layout.separator()
    layout.label(text="ComfyUI")

    # Get selected file
    if hasattr(context, "active_file"):
        directory = context.space_data.params.directory.decode('utf-8')
        filename = context.active_file.name
        filepath = os.path.join(directory, filename)

        # Import workflow
        col_workflow = layout.column()
        col_workflow.enabled = False
        if filename.lower().endswith((".json")):
            col_workflow.enabled = True
            import_workflow = col_workflow.operator("comfy.import_workflow", text="Import Workflow")
            import_workflow.filepath = filepath
            import_workflow.invoke_default = False

def register():
    """Register the panel."""

    bpy.types.FILEBROWSER_MT_context_menu.append(draw_file_browser_menu)

def unregister():
    """Unregister the panel."""

    bpy.types.FILEBROWSER_MT_context_menu.remove(draw_file_browser_menu)

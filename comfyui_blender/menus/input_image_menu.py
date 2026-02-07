"""Context menu to display additional options to set the input image."""
import bpy

from ..utils import get_inputs_folder


class ComfyBlenderInputImageMenu(bpy.types.Menu):
    """Context menu to display additional options to set the input image."""

    bl_label = ""  # Hide label
    bl_idname = "COMFY_MT_input_image_menu"

    def draw(self, context):
        layout = self.layout

        # Upload button
        layout.operator_context = "INVOKE_DEFAULT"  # This is needed to open the file browser
        upload_input_image = layout.operator("comfy.upload_input_image", text="Upload Image", icon="EXPORT")
        upload_input_image.workflow_property = context.scene.comfyui_menu_workflow_property
        layout.operator_context = "EXEC_DEFAULT" # Reset to default

        # Custom compositors
        layout.label(text="Custom Compositors", icon="NODE_COMPOSITING")

        # Check if there are any compositor node trees
        compositors = [compositor for compositor in bpy.data.node_groups if compositor.type == "COMPOSITING"]
        if not compositors:
            layout.label(text="No custom compositor found")
        else:
            # Loop over all node groups in the blend file
            for compositor in compositors:
                row = layout.row()
                custom_render = row.operator("comfy.render_custom_compositor", text=compositor.name)
                custom_render.compositor_name = compositor.name
                custom_render.workflow_property = context.scene.comfyui_menu_workflow_property

        # File browser button
        layout.separator(type="LINE")
        file_browser = layout.operator("comfy.open_file_browser", text="Open Inputs Folder", icon="FILE_FOLDER")
        file_browser.folder_path = get_inputs_folder()
        file_browser.custom_label = "Open Inputs Folder"


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderInputImageMenu)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderInputImageMenu)
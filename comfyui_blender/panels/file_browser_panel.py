"""Panel to display options in the file browser."""
import bpy

from ..utils import get_inputs_folder, get_outputs_folder, get_workflows_folder


class ComfyBlenderPanelFileBrowser(bpy.types.Panel):
    """Panel to display options in the file browser."""

    bl_label = "ComfyUI"
    bl_idname = "COMFY_PT_FileBrowser"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"
    bl_category = "ComfyUI"

    @classmethod
    def poll(cls, context):
        """Only show the panel in the file browser"""

        return context.space_data.type == "FILE_BROWSER"

    def draw(self, context):
        """Draw the panel."""

        layout = self.layout

        # Inputs folder
        inputs = layout.operator("comfy.open_file_browser", text="Inputs", icon="FILE_FOLDER")
        inputs.folder_path = get_inputs_folder()

        # Outputs folder
        outputs = layout.operator("comfy.open_file_browser", text="Outputs", icon="FILE_FOLDER")
        outputs.folder_path = get_outputs_folder()

        # Workflows folder
        workflows = layout.operator("comfy.open_file_browser", text="Workflows", icon="FILE_FOLDER")
        workflows.folder_path = get_workflows_folder()

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelFileBrowser)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelFileBrowser)

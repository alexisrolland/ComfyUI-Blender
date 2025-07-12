"""Panel to display generated outputs."""
import os

import bpy

from .. import workflow as w


class ComfyBlenderPanelOutput(bpy.types.Panel):
    """Panel to display generated outputs."""

    bl_label = "Outputs"
    bl_idname = "COMFY_PT_Output"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="IMAGE_DATA")

    def draw(self, context):
        """Draw the panel."""

        # Open file browser
        layout = self.layout
        layout.operator("comfy.open_file_browser", text="Open Outputs Folder")
        box = layout.box()

        # Get outputs collection
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        outputs_folder = str(addon_prefs.outputs_folder)
        for output in addon_prefs.outputs_collection:
            # Display output of type image
            if output.type == "image":
                # Load image in the data block if it does not exist
                if output.filename not in bpy.data.images:
                    full_path = os.path.join(outputs_folder, output.filepath)
                    bpy.data.images.load(full_path, check_existing=True)

                # Display image
                if output.filename in bpy.data.images:
                    bpy.data.images[output.filename].preview_ensure()

                    # Image preview
                    row = box.row()
                    col = row.column(align=True)
                    col.template_icon(icon_value=bpy.data.images[output.filename].preview.icon_id, scale=5)

                    # Output name with link
                    output_name = col.operator("comfy.open_image_editor", text=output.filename, emboss=False)
                    output_name.filename = output.filename

                    # Image editor
                    col = row.column(align=True)
                    image_editor = col.operator("comfy.open_image_editor", text="", icon="IMAGE")
                    image_editor.filename = output.filename

                # Delete output
                delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                delete_output.filename = output.filename
                delete_output.filepath = output.filepath
                delete_output.type = output.type

                box.separator(type="LINE")


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelOutput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelOutput)

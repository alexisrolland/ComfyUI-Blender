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

        # Get outputs information
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        outputs_folder = str(addon_prefs.outputs_folder)
        box = self.layout.box()

        # Get outputs collection
        for index, output in enumerate(reversed(addon_prefs.outputs_collection)):
            # Display output of type image
            if output.type == "image":
                # Load image in the data block if it does not exist
                if output.filename not in bpy.data.images:
                    full_path = os.path.join(outputs_folder, output.name)
                    if os.path.exists(full_path):
                        bpy.data.images.load(full_path, check_existing=True)
                    else:
                        # If the file does not exist anymore, remove it from the outputs collection
                        # To avoid error when trying to display the image
                        addon_prefs.outputs_collection.remove(index)
                        self.report({'INFO'}, f"Removed output from collection: {output.filename}")

                # Display image
                if output.filename in bpy.data.images:
                    bpy.data.images[output.filename].preview_ensure()

                    # Image preview
                    row = box.row()
                    col = row.column(align=True)
                    col.template_icon(icon_value=bpy.data.images[output.filename].preview.icon_id, scale=5)

                    # Output name operator with link
                    output_name = col.operator("comfy.open_image_editor", text=output.filename, emboss=False)
                    output_name.filename = output.filename

                    # Image editor button
                    col = row.column(align=True)
                    image_editor = col.operator("comfy.open_image_editor", text="", icon="IMAGE")
                    image_editor.filename = output.filename

                    # File browser button
                    file_browser = col.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER_LARGE")
                    file_browser.folder_path = outputs_folder

                    # Delete output button
                    delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                    delete_output.filename = output.filename
                    delete_output.filepath = output.name
                    delete_output.type = output.type

                box.separator(type="LINE")

            # Display output of type 3d
            if output.type == "3d":
                full_path = os.path.join(outputs_folder, output.name)
                if os.path.exists(full_path):
                    # Create UI elements for 3D output
                    row = box.row()
                    col = row.column(align=True)

                    # Output name operator with link
                    output_name = col.operator("comfy.import_3d_model", text=output.filename, emboss=False, icon="OUTLINER_OB_MESH")
                    output_name.filepath = full_path

                    # Import 3D model button
                    col = row.column(align=True)
                    import_model = col.operator("comfy.import_3d_model", text="", icon="IMPORT")
                    import_model.filepath = full_path

                    # File browser button
                    file_browser = col.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER_LARGE")
                    file_browser.folder_path = outputs_folder

                    # Delete output button
                    delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                    delete_output.filename = output.filename
                    delete_output.filepath = output.name
                    delete_output.type = output.type

                else:
                    # If the file does not exist anymore, remove it from the outputs collection
                    # To avoid error when trying to display the image
                    addon_prefs.outputs_collection.remove(index)
                    self.report({'INFO'}, f"Removed output from collection: {output.filename}")

                box.separator(type="LINE")

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelOutput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelOutput)

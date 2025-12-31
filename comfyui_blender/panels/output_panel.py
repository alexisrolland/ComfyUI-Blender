"""Panel to display generated outputs."""
import os

import bpy

from ..utils import get_outputs_folder


class ComfyBlenderPanelOutput(bpy.types.Panel):
    """Panel to display generated outputs."""

    bl_label = "Outputs"
    bl_region_type = "UI"
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        # Display custom title with number of outputs
        project_settings = bpy.context.scene.comfyui_project_settings
        outputs_collection = project_settings.outputs_collection
        self.layout.label(icon="IMAGE_DATA")
        self.bl_label = f"Outputs ({len(outputs_collection)})"

    def draw(self, context):
        """Draw the panel."""

        # Get outputs folder
        outputs_folder = get_outputs_folder()

        # Get outputs collection
        project_settings = bpy.context.scene.comfyui_project_settings
        outputs_collection = project_settings.outputs_collection

        # Switch output layout to list
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        output_layout = row.operator("comfy.switch_output_layout", text="", icon="LONGDISPLAY")
        output_layout.layout_type = "list"

        # Switch output layout to thumbnail
        output_layout = row.operator("comfy.switch_output_layout", text="", icon="IMGDISPLAY")
        output_layout.layout_type = "thumbnail"

        # File browser button
        file_browser = row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER")
        file_browser.folder_path = outputs_folder
        file_browser.custom_label = "Open Outputs Folder"

        # Create a box with grid flow for all outputs
        box = self.layout.box()

        # Display message when outputs collection is empty
        if len(outputs_collection) == 0:
            box.label(text="No output generated yet")
            return

        # Display outputs as thumbnails
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        if addon_prefs.outputs_layout == "thumbnail":
            flow = box.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)
            for index, output in enumerate(reversed(outputs_collection)):
                # Display output only if file still exists
                full_path = os.path.join(outputs_folder, output.filepath)
                if os.path.exists(full_path):
                    card = flow.column(align=True)

                    # Display output of type image
                    if output.type == "image":
                        # Check if image exists in the data block
                        image = None
                        for i in bpy.data.images:
                            if i.filepath == full_path:
                                image = i
                                break

                        # Load image in the data block if it does not exist
                        if image is None and os.path.exists(full_path):
                            image = bpy.data.images.load(full_path, check_existing=True)
                            image.preview_ensure()

                        if image:
                            # Output preview
                            row = card.row(align=True)
                            row.template_icon(icon_value=image.preview.icon_id, scale=5)

                            # Image editor button
                            col = row.column(align=True)
                            image_editor = col.operator("comfy.open_image_editor", text="", icon="IMAGE")
                            image_editor.name = image.name

                            # Delete output button
                            if addon_prefs.confirm_delete_output:
                                delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                            else:
                                delete_output = col.operator("comfy.delete_output_ok", text="", icon="TRASH")
                            delete_output.name = output.name
                            delete_output.filepath = output.filepath
                            delete_output.type = output.type

                            # Output menu button
                            output_menu = col.operator("comfy.show_output_menu", text="", icon="DOWNARROW_HLT")
                            output_menu.output_type = output.type
                            output_menu.output_name = image.name
                            output_menu.output_filepath = image.filepath

                            # Output name with link
                            output_name = card.operator("comfy.open_image_editor", text=image.name, emboss=False)
                            output_name.name = image.name

                    # Display output of type 3d
                    elif output.type == "3d":
                        # Load 3D model icon in the data block if it does not exist
                        if "icon_mesh_data.png" not in bpy.data.images:
                            addon_folder = os.path.dirname(os.path.dirname(__file__))
                            icon_path = os.path.join(addon_folder, "assets", "icon_mesh_data.png")
                            if os.path.exists(icon_path):
                                bpy.data.images.load(icon_path, check_existing=True)

                        bpy.data.images["icon_mesh_data.png"].preview_ensure()
                        icon_id = bpy.data.images["icon_mesh_data.png"].preview.icon_id

                        # Output preview
                        row = card.row(align=True)
                        row.template_icon(icon_value=icon_id, scale=5)

                        # Import 3D model button
                        col = row.column(align=True)
                        import_model = col.operator("comfy.import_3d_model", text="", icon="IMPORT")
                        import_model.filepath = full_path

                        # Delete output button
                        if addon_prefs.confirm_delete_output:
                            delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                        else:
                            delete_output = col.operator("comfy.delete_output_ok", text="", icon="TRASH")
                        delete_output.name = output.name
                        delete_output.filepath = output.filepath
                        delete_output.type = output.type

                        # Output menu button
                        output_menu = col.operator("comfy.show_output_menu", text="", icon="DOWNARROW_HLT")
                        output_menu.output_type = output.type
                        output_menu.output_name = output.name
                        output_menu.output_filepath = full_path

                        # Output name with link
                        output_name = card.operator("comfy.import_3d_model", text=output.name, emboss=False)
                        output_name.filepath = full_path
                    
                    # Display output of type text
                    elif output.type == "text":
                        # Load text icon in the data block if it does not exist
                        if "icon_file_text.png" not in bpy.data.images:
                            addon_folder = os.path.dirname(os.path.dirname(__file__))
                            icon_path = os.path.join(addon_folder, "assets", "icon_file_text.png")
                            if os.path.exists(icon_path):
                                bpy.data.images.load(icon_path, check_existing=True)

                        bpy.data.images["icon_file_text.png"].preview_ensure()
                        icon_id = bpy.data.images["icon_file_text.png"].preview.icon_id

                        # Check if text object exists in the data block
                        text = None
                        for i in bpy.data.texts:
                            if i.filepath == full_path:
                                text = i
                                break

                        # Load text object in the data block if it does not exist
                        if text is None and os.path.exists(full_path):
                            text = bpy.data.texts.load(full_path)

                        if text:
                            # Output preview
                            row = card.row(align=True)
                            row.template_icon(icon_value=icon_id, scale=5)

                            # Text editor button
                            col = row.column(align=True)
                            text_editor = col.operator("comfy.open_text_editor", text="", icon="TEXT")
                            text_editor.name = text.name
                            text_editor.workflow_property = ""  # Ensure this is empty to avoid setting inputs

                            # Delete output button
                            if addon_prefs.confirm_delete_output:
                                delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                            else:
                                delete_output = col.operator("comfy.delete_output_ok", text="", icon="TRASH")
                            delete_output.name = output.name
                            delete_output.filepath = output.filepath
                            delete_output.type = output.type

                            # Output menu button
                            output_menu = col.operator("comfy.show_output_menu", text="", icon="DOWNARROW_HLT")
                            output_menu.output_type = output.type
                            output_menu.output_name = output.name
                            output_menu.output_filepath = full_path

                            # Output name with link
                            output_name = card.operator("comfy.open_text_editor", text=text.name, emboss=False)
                            output_name.name = text.name
                            output_name.workflow_property = ""  # Ensure this is empty to avoid setting inputs

                else:
                    # If the file does not exist anymore, remove it from the outputs collection
                    # Schedule delete after draw
                    def remove_output(name=output.name, filepath=output.filepath, type=output.type):
                        bpy.ops.comfy.delete_output_ok(name=name, filepath=filepath, type=type)
                    bpy.app.timers.register(remove_output, first_interval=0.00)

        # Display outputs as list
        elif addon_prefs.outputs_layout == "list":
            for index, output in enumerate(reversed(outputs_collection)):
                # Display output only if file still exists
                full_path = os.path.join(outputs_folder, output.filepath)
                if os.path.exists(full_path):
                    row = box.row(align=True)
                    row_left = row.row(align=True)
                    row_left.alignment = "LEFT"
                    row_right = row.row(align=True)
                    row_right.alignment = "RIGHT"

                    # Display output of type image
                    if output.type == "image":
                        # Check if image exists in the data block
                        image = None
                        for i in bpy.data.images:
                            if i.filepath == full_path:
                                image = i
                                break

                        # Load image in the data block if it does not exist
                        if image is None and os.path.exists(full_path):
                            image = bpy.data.images.load(full_path, check_existing=True)

                        if image:
                            # Output name with link
                            output_name = row_left.operator("comfy.open_image_editor", text=image.name, emboss=False, icon="IMAGE_DATA")
                            output_name.name = image.name

                            # Image editor button
                            image_editor = row_right.operator("comfy.open_image_editor", text="", icon="IMAGE")
                            image_editor.name = image.name

                            # Delete output button
                            if addon_prefs.confirm_delete_output:
                                delete_output = row_right.operator("comfy.delete_output", text="", icon="TRASH")
                            else:
                                delete_output = row_right.operator("comfy.delete_output_ok", text="", icon="TRASH")
                            delete_output.name = output.name
                            delete_output.filepath = output.filepath
                            delete_output.type = output.type

                            # Output menu button
                            output_menu = row_right.operator("comfy.show_output_menu", text="", icon="DOWNARROW_HLT")
                            output_menu.output_type = output.type
                            output_menu.output_name = image.name
                            output_menu.output_filepath = image.filepath

                    # Display output of type 3d
                    elif output.type == "3d":
                        # Output name with link
                        output_name = row_left.operator("comfy.import_3d_model", text=output.name, emboss=False, icon="MESH_DATA")
                        output_name.filepath = full_path

                        # Import 3D model button
                        import_model = row_right.operator("comfy.import_3d_model", text="", icon="IMPORT")
                        import_model.filepath = full_path

                        # Delete output button
                        if addon_prefs.confirm_delete_output:
                            delete_output = row_right.operator("comfy.delete_output", text="", icon="TRASH")
                        else:
                            delete_output = row_right.operator("comfy.delete_output_ok", text="", icon="TRASH")
                        delete_output.name = output.name
                        delete_output.filepath = output.filepath
                        delete_output.type = output.type

                        # Output menu button
                        output_menu = row_right.operator("comfy.show_output_menu", text="", icon="DOWNARROW_HLT")
                        output_menu.output_type = output.type
                        output_menu.output_name = output.name
                        output_menu.output_filepath = full_path
                    
                    # Display output of type text
                    elif output.type == "text":
                        # Check if text object exists in the data block
                        text = None
                        for i in bpy.data.texts:
                            if i.filepath == full_path:
                                text = i
                                break
                        
                        # Load text object in the data block if it does not exist
                        if text is None and os.path.exists(full_path):
                            text = bpy.data.texts.load(full_path)

                        if text:
                            # Output name with link
                            output_name = row_left.operator("comfy.open_text_editor", text=text.name, emboss=False, icon="FILE_TEXT")
                            output_name.name = text.name
                            output_name.workflow_property = ""  # Ensure this is empty to avoid setting inputs

                            # Text editor button
                            text_editor = row_right.operator("comfy.open_text_editor", text="", icon="TEXT")
                            text_editor.name = text.name
                            output_name.workflow_property = ""  # Ensure this is empty to avoid setting inputs

                            # Delete output button
                            if addon_prefs.confirm_delete_output:
                                delete_output = row_right.operator("comfy.delete_output", text="", icon="TRASH")
                            else:
                                delete_output = row_right.operator("comfy.delete_output_ok", text="", icon="TRASH")
                            delete_output.name = output.name
                            delete_output.filepath = output.filepath
                            delete_output.type = output.type

                            # Output menu button
                            output_menu = row_right.operator("comfy.show_output_menu", text="", icon="DOWNARROW_HLT")
                            output_menu.output_type = output.type
                            output_menu.output_name = output.name
                            output_menu.output_filepath = full_path

                else:
                    # If the file does not exist anymore, remove it from the outputs collection
                    # Schedule delete after draw
                    def remove_output(name=output.name, filepath=output.filepath, type=output.type):
                        bpy.ops.comfy.delete_output_ok(name=name, filepath=filepath, type=type)
                    bpy.app.timers.register(remove_output, first_interval=0.00)


class ComfyBlenderPanelOutput3DViewer(ComfyBlenderPanelOutput, bpy.types.Panel):
    """Class to display the panel in the 3D viewer."""

    bl_idname = "COMFY_PT_Output_3DViewer"
    bl_space_type = "VIEW_3D"


class ComfyBlenderPanelOutputImageEditor(ComfyBlenderPanelOutput, bpy.types.Panel):
    """Class to display the panel in the image editor."""

    bl_idname = "COMFY_PT_Output_ImageEditor"
    bl_space_type = "IMAGE_EDITOR"


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelOutput3DViewer)
    bpy.utils.register_class(ComfyBlenderPanelOutputImageEditor)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelOutput3DViewer)
    bpy.utils.unregister_class(ComfyBlenderPanelOutputImageEditor)

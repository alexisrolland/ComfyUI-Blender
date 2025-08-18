"""Panel to display generated outputs."""
import os

import bpy


class ComfyBlenderPanelOutput(bpy.types.Panel):
    """Panel to display generated outputs."""

    bl_label = "Outputs"
    bl_idname = "COMFY_PT_Output"
    bl_space_type = "VIEW_3D"
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
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        outputs_folder = str(addon_prefs.outputs_folder)

        # Get outputs collection
        project_settings = bpy.context.scene.comfyui_project_settings
        outputs_collection = project_settings.outputs_collection

        # File browser button
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        file_browser = row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER")
        file_browser.folder_path = outputs_folder
        file_browser.custom_label = "Open Outputs Folder"

        # Switch output layout to list
        output_layout = row.operator("comfy.switch_output_layout", text="", icon="LONGDISPLAY")
        output_layout.layout_type = "list"

        # Switch output layout to thumbnail
        output_layout = row.operator("comfy.switch_output_layout", text="", icon="IMGDISPLAY")
        output_layout.layout_type = "thumbnail"

        # Create a box with grid flow for all outputs
        box = self.layout.box()

        # Display message when outputs collection is empty
        if len(outputs_collection) == 0:
            box.label(text="No output generated yet")
            return

        # Display outputs as thumbnails
        if addon_prefs.outputs_layout == "thumbnail":
            flow = box.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)

            # Get outputs collection
            for index, output in enumerate(reversed(outputs_collection)):
                card = flow.column(align=True)

                # Display output of type image
                if output.type == "image":
                    full_path = os.path.join(outputs_folder, output.name)

                    # Load image in the data block if it does not exist
                    if output.filename not in bpy.data.images:
                        if os.path.exists(full_path):
                            bpy.data.images.load(full_path, check_existing=True)
                        else:
                            # If the file does not exist anymore, remove it from the outputs collection
                            # To avoid error when trying to display the image
                            outputs_collection.remove(index)

                    # Display image
                    if output.filename in bpy.data.images:
                        bpy.data.images[output.filename].preview_ensure()
                        icon_id = bpy.data.images[output.filename].preview.icon_id

                        # Image preview
                        row = card.row(align=True)
                        row.template_icon(icon_value=icon_id, scale=5)

                        # Image editor button
                        col = row.column(align=True)
                        image_editor = col.operator("comfy.open_image_editor", text="", icon="IMAGE")
                        image_editor.filename = output.filename

                        # Reload workflow button
                        import_workflow = col.operator("comfy.import_workflow", text="", icon="NODETREE")
                        import_workflow.filepath = full_path
                        import_workflow.invoke_default = False

                        # Delete output button
                        delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                        delete_output.filename = output.filename
                        delete_output.filepath = output.name
                        delete_output.type = output.type

                        # Output name with link
                        output_name = card.operator("comfy.open_image_editor", text=output.filename, emboss=False)
                        output_name.filename = output.filename

                # Display output of type 3d
                elif output.type == "3d":
                    full_path = os.path.join(outputs_folder, output.name)

                    # Load 3D model icon in the data block if it does not exist
                    if "icon_mesh_data.png" not in bpy.data.images:
                        addon_folder = os.path.dirname(os.path.dirname(__file__))
                        icon_path = os.path.join(addon_folder, "assets", "icon_mesh_data.png")
                        if os.path.exists(icon_path):
                            bpy.data.images.load(icon_path, check_existing=True)

                    # Display 3D model
                    if os.path.exists(full_path):
                        bpy.data.images["icon_mesh_data.png"].preview_ensure()
                        icon_id = bpy.data.images["icon_mesh_data.png"].preview.icon_id

                        # Image preview
                        row = card.row(align=True)
                        row.template_icon(icon_value=icon_id, scale=5)

                        # Import 3D model button
                        col = row.column(align=True)
                        import_model = col.operator("comfy.import_3d_model", text="", icon="IMPORT")
                        import_model.filepath = full_path

                        # Delete output button
                        delete_output = col.operator("comfy.delete_output", text="", icon="TRASH")
                        delete_output.filename = output.filename
                        delete_output.filepath = output.name
                        delete_output.type = output.type

                        # Output name with link
                        output_name = card.operator("comfy.import_3d_model", text=output.filename, emboss=False)
                        output_name.filepath = full_path
                    else:
                        # If the file does not exist anymore, remove it from the outputs collection
                        # To avoid error when trying to display the image
                        outputs_collection.remove(index)

        # Display outputs as list
        elif addon_prefs.outputs_layout == "list":
            for index, output in enumerate(reversed(outputs_collection)):
                row = box.row(align=True)
                row_left = row.row(align=True)
                row_left.alignment = "LEFT"
                row_right = row.row(align=True)
                row_right.alignment = "RIGHT"

                # Display output of type image
                if output.type == "image":
                    full_path = os.path.join(outputs_folder, output.name)

                    # Load image in the data block if it does not exist
                    if output.filename not in bpy.data.images:
                        if os.path.exists(full_path):
                            bpy.data.images.load(full_path, check_existing=True)
                        else:
                            # If the file does not exist anymore, remove it from the outputs collection
                            # To avoid error when trying to display the image
                            outputs_collection.remove(index)

                    # Display image
                    if output.filename in bpy.data.images:
                        # Output name with link
                        output_name = row_left.operator("comfy.open_image_editor", text=output.filename, emboss=False, icon="IMAGE_DATA")
                        output_name.filename = output.filename

                        # Image editor button
                        image_editor = row_right.operator("comfy.open_image_editor", text="", icon="IMAGE")
                        image_editor.filename = output.filename

                        # Reload workflow button
                        import_workflow = row_right.operator("comfy.import_workflow", text="", icon="NODETREE")
                        import_workflow.filepath = full_path
                        import_workflow.invoke_default = False

                # Display output of type 3d
                elif output.type == "3d":
                    full_path = os.path.join(outputs_folder, output.name)

                    # Display 3D model
                    if os.path.exists(full_path):
                        # Output name with link
                        output_name = row_left.operator("comfy.import_3d_model", text=output.filename, emboss=False, icon="MESH_DATA")
                        output_name.filepath = full_path

                        # Import 3D model button
                        import_model = row_right.operator("comfy.import_3d_model", text="", icon="IMPORT")
                        import_model.filepath = full_path
                    else:
                        # If the file does not exist anymore, remove it from the outputs collection
                        # To avoid error when trying to display the image
                        outputs_collection.remove(index)

                # Delete output button
                delete_output = row_right.operator("comfy.delete_output", text="", icon="TRASH")
                delete_output.filename = output.filename
                delete_output.filepath = output.name
                delete_output.type = output.type

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelOutput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelOutput)

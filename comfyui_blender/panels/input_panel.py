"""Panel to display a workflow inputs."""
import json
import os

import bpy

from .. import workflow as w


class ComfyBlenderPanelInput(bpy.types.Panel):
    """Panel to display a workflow inputs."""

    bl_label = "Inputs"
    bl_idname = "COMFY_PT_Input"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="EXPERIMENTAL")

    def draw(self, context):
        """Draw the panel."""

        layout = self.layout
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        if addon_prefs.connection_status:
            if hasattr(context.scene, "current_workflow"):
                # Get the selected workflow
                workflows_folder = str(addon_prefs.workflows_folder)
                workflow_filename = str(addon_prefs.workflow)
                workflow_path = os.path.join(workflows_folder, workflow_filename)
                current_workflow = context.scene.current_workflow

                # Load the workflow JSON file
                if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
                    with open(workflow_path, "r",  encoding="utf-8") as file:
                        workflow = json.load(file)

                    # Get sorted inputs from the workflow
                    inputs = w.parse_workflow_for_inputs(workflow)

                    # Display workflow input properties
                    for key, node in inputs.items():
                        property_name = f"node_{key}"

                        # Custom handling for group of inputs
                        if node["class_type"] == "BlenderInputGroup":
                            col = layout.column()
                            if node["inputs"].get("show_title", False):
                                # Get the input name from the workflow properties
                                name = current_workflow.bl_rna.properties[property_name].name  # Node title
                                col.label(text=name + ":")

                            # Create box for the group
                            group_box = col.box()
                            if node["inputs"].get("compact", False):
                                group_col = group_box.column(align=True)
                            else:
                                group_col = group_box.column()

                            # Display group inputs
                            group_inputs = getattr(current_workflow, property_name)
                            for input_key in group_inputs:
                                # Empty groups without children nodes have a dummy key -1
                                # Skip the dummy key
                                if int(input_key) > 0:
                                    group_property_name = f"node_{input_key}"
                                    self.display_input(context, current_workflow, group_col, group_property_name, inputs[str(input_key)], is_root=False)

                        else:
                            # Skip input if it belongs to a group
                            if "group" not in node["inputs"]:
                                self.display_input(context, current_workflow, layout, property_name, node)

                    # Add run workflow button
                    col = layout.column()
                    col.scale_y = 1.5
                    col.operator("comfy.run_workflow", text="Run Workflow", icon="PLAY")
        else:
            # Create a box with grid flow for all outputs
            box = layout.box()
            box.label(text="Connect to the ComfyUI server to display workflow inputs.")

    def display_input(self, context, current_workflow, layout, property_name, node, is_root=True):
        """Format the input for display in the panel."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        inputs_folder = str(addon_prefs.inputs_folder)

        # Custom handling for integer inputs
        if node["class_type"] == "BlenderInputInt":
            row = layout.row(align=True)
            row.prop(current_workflow, property_name)

            # Set / get camera width
            if node["inputs"].get("camera_width", False):
                set_width = row.operator("comfy.set_camera_resolution", text="", icon="CAMERA_DATA")
                set_width.value = current_workflow.get(property_name, node["inputs"].get("default", 0))
                set_width.axis = "X"

                get_width = row.operator("comfy.get_camera_resolution", text="", icon="IMAGE_DATA")
                get_width.property_name = property_name
                get_width.axis = "X"

            # Set / get camera height
            if node["inputs"].get("camera_height", False):
                set_height = row.operator("comfy.set_camera_resolution", text="", icon="CAMERA_DATA")
                set_height.value = current_workflow.get(property_name, node["inputs"].get("default", 0))
                set_height.axis = "Y"

                get_width = row.operator("comfy.get_camera_resolution", text="", icon="IMAGE_DATA")
                get_width.property_name = property_name
                get_width.axis = "Y"

        # Custom handling for 3D model inputs
        elif node["class_type"] == "BlenderInputLoad3D":
            # Add box only for main layout
            box = layout.box() if is_root else layout

            # Get the input name from the workflow properties
            name = current_workflow.bl_rna.properties[property_name].name  # Node title
            row = box.row(align=True)
            row.label(text=name + ":")

            # Prepare GLB file
            prepare_glb = row.operator("comfy.prepare_glb_file", text="glb", icon="MESH_DATA")
            prepare_glb.workflow_property = property_name

            # Prepare OBJ file
            prepare_obj = row.operator("comfy.prepare_obj_file", text="obj", icon="MESH_DATA")
            prepare_obj.workflow_property = property_name

            # File browser button
            file_browser = row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER")
            file_browser.folder_path = inputs_folder
            file_browser.custom_label = "Open Inputs Folder"

            # Get the input file name from the workflow class
            input_filepath = getattr(current_workflow, property_name)
            input_fullpath = os.path.join(inputs_folder, input_filepath)
            input_name = os.path.basename(input_filepath)

            # Display prepared 3D model
            if input_name:
                # 3D model name with link
                row = box.row()
                input = row.operator("comfy.import_3d_model", text=input_name, emboss=False, icon="MESH_DATA")
                input.filepath = input_fullpath

                # Delete input button
                sub_row = row.row(align=True)
                delete_input = sub_row.operator("comfy.delete_input", text="", icon="TRASH")
                delete_input.name = input_name
                delete_input.filepath = input_filepath
                delete_input.workflow_property = property_name
                delete_input.type = "3d"

        # Custom handling for image inputs
        elif node["class_type"] == "BlenderInputLoadImage":
            # Get the input name from the workflow properties
            row = layout.row(align=True)
            name = current_workflow.bl_rna.properties[property_name].name  # Node title
            row.label(text=name + ":")

            # Upload button
            upload_input_image = row.operator("comfy.upload_input_image", text="", icon="EXPORT")
            upload_input_image.workflow_property = property_name

            # Render view
            render_view = row.operator("comfy.render_view", text="", icon="OUTPUT")
            render_view.workflow_property = property_name

            # Render depth map
            render_depth = row.operator("comfy.render_depth_map", text="", icon="MATERIAL")
            render_depth.workflow_property = property_name

            # Render lineart
            render_lineart = row.operator("comfy.render_lineart", text="", icon="SHADING_WIRE")
            render_lineart.workflow_property = property_name

            # File browser button
            file_browser = row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER")
            file_browser.folder_path = inputs_folder
            file_browser.custom_label = "Open Inputs Folder"

            # Add box only if input is not in a group/box
            box = layout.box() if is_root else layout

            # Get input image from the workflow property
            image = getattr(current_workflow, property_name)

            # Display input image
            if image:
                row = box.row()

                # Image preview
                bpy.data.images[image.name].preview_ensure()
                row = box.row()
                row.template_icon(icon_value=bpy.data.images[image.name].preview.icon_id, scale=5)
                label_image = box.operator("comfy.open_image_editor", text=image.name, emboss=False)
                label_image.name = image.name

                # Open image editor button
                col = row.column(align=True)
                open_image = col.operator("comfy.open_image_editor", text="", icon="IMAGE")
                open_image.name = image.name
                
                # Delete input button
                delete_input = col.operator("comfy.delete_input", text="", icon="TRASH")
                delete_input.name = image.name
                delete_input.filepath = image.filepath
                delete_input.workflow_property = property_name
                delete_input.type = "image"

        # Custom handling for mask inputs
        # Mask inputs are images with alpha channel
        elif node["class_type"] == "BlenderInputLoadMask":
            # Get the input name from the workflow properties
            row = layout.row(align=True)
            name = current_workflow.bl_rna.properties[property_name].name  # Node title
            row.label(text=name + ":")

            # Upload button
            upload_input_image = row.operator("comfy.upload_input_image", text="", icon="EXPORT")
            upload_input_image.workflow_property = property_name

            # File browser button
            file_browser = row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER")
            file_browser.folder_path = inputs_folder
            file_browser.custom_label = "Open Inputs Folder"

            # Add box only for main layout
            box = layout.box() if is_root else layout

            # Selected image
            #box.prop(current_workflow, property_name, text="", icon="IMAGE_DATA")
            #search_image = row.operator("comfy.search_image", text="", icon="IMAGE_DATA")
            #search_image.workflow_property = property_name

            # Get input image from the workflow property
            image = getattr(current_workflow, property_name)

            # Display input image
            if image:
                row = box.row()

                # Image preview
                bpy.data.images[image.name].preview_ensure()
                row = box.row()
                row.template_icon(icon_value=bpy.data.images[image.name].preview.icon_id, scale=5)
                label_image = box.operator("comfy.open_image_editor", text=image.name, emboss=False)
                label_image.name = image.name

                # Open image editor button
                col = row.column(align=True)
                open_image = col.operator("comfy.open_image_editor", text="", icon="IMAGE")
                open_image.name = image.name
                
                # Delete input button
                delete_input = col.operator("comfy.delete_input", text="", icon="TRASH")
                delete_input.name = image.name
                delete_input.filepath = image.filepath
                delete_input.workflow_property = property_name
                delete_input.type = "image"

        # Custom handling for seed inputs
        elif node["class_type"] == "BlenderInputSeed":
            row = layout.row(align=True)
            row.prop(current_workflow, property_name)
            
            # Get random seed button
            random_seed = row.operator("comfy.get_random_seed", text="", icon="FILE_REFRESH")
            random_seed.workflow_property = property_name

            # Lock seed toggle
            if addon_prefs.lock_seed:
                row.prop(addon_prefs, "lock_seed", text="", icon="LOCKED")
            else:
                row.prop(addon_prefs, "lock_seed", text="", icon="UNLOCKED")

        elif node["class_type"] == "BlenderInputStringMultiline":
            row = layout.row(align=True)
            row.prop(current_workflow, property_name)

            # Edit text button
            open_text = row.operator("comfy.open_text_editor", text="", icon="GREASEPENCIL")
            open_text.workflow_property = property_name

            # Get input text from the workflow property
            text = getattr(current_workflow, property_name)

            # Delete input button
            row = row.row(align=True)
            row.enabled = True if text else False
            delete_input = row.operator("comfy.delete_input", text="", icon="TRASH")
            delete_input.name = text.name if text else ""
            delete_input.workflow_property = property_name
            delete_input.type = "text"

        else:
            # Default display for other input types
            layout.prop(current_workflow, property_name)


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelInput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelInput)

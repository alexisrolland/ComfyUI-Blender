"""Panel to display a workflow inputs."""
import json
import os

import bpy

from .. import workflow as w


class ComfyBlenderPanelInput(bpy.types.Panel):
    """Panel to display a workflow inputs."""

    bl_label = "Inputs"
    bl_idname = "COMFY_PT_Input"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="EXPERIMENTAL")

    def draw(self, context):
        """Draw the panel."""

        # Get the selected workflow
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_filename)
        inputs_folder = str(addon_prefs.inputs_folder)

        # Load the workflow JSON file
        if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
            box = self.layout.box()
            with open(workflow_path, "r",  encoding="utf-8") as file:
                workflow = json.load(file)

            # Get sorted inputs from the workflow
            inputs = w.parse_workflow_for_inputs(workflow)

            # Display workflow input properties
            current_workflow = context.scene.current_workflow
            for key, node in inputs.items():
                property_name = f"node_{key}"

                # Custom handling for image inputs
                if node["class_type"] == "BlenderInputLoadImage":
                    # Get the input name from the workflow properties
                    name = current_workflow.bl_rna.properties[property_name].name  # Node title
                    row = box.row(align=True)
                    row.label(text=name + ":")

                    # Import input button
                    import_input = row.operator("comfy.import_input", text="", icon="IMPORT")
                    import_input.workflow_property = property_name

                    # Render view
                    render_view = row.operator("comfy.render_view", text="", icon="OUTPUT")
                    render_view.workflow_property = property_name

                    # Render depth map
                    render_depth = row.operator("comfy.render_depth_map", text="", icon="MATERIAL")
                    render_depth.workflow_property = property_name

                    # Get the input file name from the workflow class
                    input_filepath = getattr(current_workflow, property_name)
                    input_filename = os.path.basename(input_filepath)

                    # Display imported input image if it exists
                    if input_filename in bpy.data.images:
                        bpy.data.images[input_filename].preview_ensure()

                        # Image preview
                        row = box.row()
                        col = row.column(align=True)
                        col.template_icon(icon_value=bpy.data.images[input_filename].preview.icon_id, scale=5)

                        # Input name operator with link
                        input_name = col.operator("comfy.open_image_editor", text=input_filename, emboss=False)
                        input_name.filename = input_filename

                        # Image editor button
                        col = row.column(align=True)
                        image_editor = col.operator("comfy.open_image_editor", text="", icon="IMAGE")
                        image_editor.filename = input_filename

                        file_browser = col.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER_LARGE")
                        file_browser.folder_path = inputs_folder

                        # Delete input button
                        delete_input = col.operator("comfy.delete_input", text="", icon="TRASH")
                        delete_input.filename = input_filename
                        delete_input.workflow_property = property_name
                        delete_input.type = "image"

                # Custom handling for seed inputs
                elif node["class_type"] == "BlenderInputSeed":
                    row = box.row(align=True)
                    row.prop(current_workflow, property_name) # Random seed management to be implemented
                    if addon_prefs.lock_seed:
                        row.prop(addon_prefs, "lock_seed", text="", icon="LOCKED")
                    else:
                        row.prop(addon_prefs, "lock_seed", text="", icon="UNLOCKED")

                else:
                    # Default display for other input types
                    box.prop(current_workflow, property_name)

            # Add run workflow button
            col = box.column()
            col.scale_y = 1.5
            col.operator("comfy.run_workflow", text="Run Workflow", icon="PLAY")

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelInput)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelInput)

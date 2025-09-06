"""Context menu to provide custom actions for outputs."""
import os

import bpy


class ComfyBlenderOutputMenu(bpy.types.Menu):
    """Context menu to provide custom actions for outputs."""
    
    bl_label = ""  # Hide label
    bl_idname = "COMFY_MT_output_menu"
    
    def draw(self, context):
        layout = self.layout

        # Get output data from scene properties
        output_type = context.scene.comfyui_menu_output_type
        output_name = context.scene.comfyui_menu_output_name
        output_filepath = context.scene.comfyui_menu_output_filepath
        print(f"Output Menu: type={output_type}, name={output_name}, filepath={output_filepath}")

        # Import image button
        row = layout.row()
        row.enabled = output_type == "image"
        import_image = row.operator("comfy.import_image", text="Import Image", icon="IMPORT")
        import_image.name = output_name

        # Project material button
        row = layout.row()
        row.enabled = output_type == "image"
        project_material = row.operator("comfy.project_material", text="Project Material", icon="SHADING_TEXTURE")
        project_material.name = output_name

        # Reload workflow button
        row = layout.row()
        row.enabled = True  # Enabled for both image and 3d outputs
        import_workflow = row.operator("comfy.import_workflow", text="Import Workflow", icon="NODETREE")
        import_workflow.filepath = output_filepath
        import_workflow.invoke_default = False


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderOutputMenu)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderOutputMenu)
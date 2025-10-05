"""Context menu to provide custom actions for outputs."""
import bpy

from ..workflow import get_current_workflow_target_inputs

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

        # Send to input
        layout.separator(type="LINE")
        layout.label(text="Send to Input", icon="INDIRECT_ONLY_OFF")
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        if addon_prefs.connection_status:
            target_inputs = get_current_workflow_target_inputs(self, context)
            for input in target_inputs:
                row = layout.row()
                row.enabled = output_type == "image"
                send_to_input = row.operator("comfy.send_to_input", text=input[1])  # Target input name
                send_to_input.name = output_name
                send_to_input.workflow_property = input[0]  # Target input property_name
        else:
            layout.label(text="Connect to the ComfyUI server to display workflow inputs.")


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderOutputMenu)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderOutputMenu)
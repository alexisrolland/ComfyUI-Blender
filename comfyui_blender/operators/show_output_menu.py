"""Operator to display the output menu."""
import bpy


class ComfyBlenderOperatorShowOutputMenu(bpy.types.Operator):
    """Operator to display the output menu."""

    bl_idname = "comfy.show_output_menu"
    bl_label = "Show Output Menu"
    bl_description = "Display the output menu."

    output_type: bpy.props.StringProperty()
    output_name: bpy.props.StringProperty()
    output_filepath: bpy.props.StringProperty()

    def execute(self, context):
        """Execute the operator."""

        # Store output data in scene properties for the menu to access
        scene = context.scene
        scene.comfyui_menu_output_type = self.output_type
        scene.comfyui_menu_output_name = self.output_name
        scene.comfyui_menu_output_filepath = self.output_filepath

        # Show the context menu
        bpy.ops.wm.call_menu(name="COMFY_MT_output_menu")
        return {'FINISHED'}


def register():
    """Register the operator."""

    # Register scene properties for menu data
    bpy.types.Scene.comfyui_menu_output_type = bpy.props.StringProperty()
    bpy.types.Scene.comfyui_menu_output_name = bpy.props.StringProperty()
    bpy.types.Scene.comfyui_menu_output_filepath = bpy.props.StringProperty()
    bpy.utils.register_class(ComfyBlenderOperatorShowOutputMenu)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorShowOutputMenu)
    del bpy.types.Scene.comfyui_menu_output_type
    del bpy.types.Scene.comfyui_menu_output_name
    del bpy.types.Scene.comfyui_menu_output_filepath

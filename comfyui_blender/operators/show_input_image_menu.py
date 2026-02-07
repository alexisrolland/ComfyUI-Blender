"""Operator to display the input image menu."""
import bpy


class ComfyBlenderOperatorShowInputImageMenu(bpy.types.Operator):
    """Operator to display the input image menu."""

    bl_idname = "comfy.show_input_image_menu"
    bl_label = "Show Input Image Menu"
    bl_description = "Display additional options to set the input image."

    workflow_property: bpy.props.StringProperty()

    def execute(self, context):
        """Execute the operator."""

        # Store workflow property in scene properties for the menu to access
        scene = context.scene
        scene.comfyui_menu_workflow_property = self.workflow_property

        # Show the context menu
        bpy.ops.wm.call_menu(name="COMFY_MT_input_image_menu")
        return {'FINISHED'}


def register():
    """Register the operator."""

    # Register scene properties for menu data
    bpy.types.Scene.comfyui_menu_workflow_property = bpy.props.StringProperty()

    bpy.utils.register_class(ComfyBlenderOperatorShowInputImageMenu)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorShowInputImageMenu)

    # Check if attributes exist before deleting them
    if hasattr(bpy.types.Scene, "comfyui_menu_workflow_property"):
        del bpy.types.Scene.comfyui_menu_workflow_property

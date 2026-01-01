"""Operator to display the custom compositor menu."""
import bpy


class ComfyBlenderOperatorShowCustomCompositorMenu(bpy.types.Operator):
    """Operator to display the custom compositor menu."""

    bl_idname = "comfy.show_custom_compositor_menu"
    bl_label = "Show Custom Compositor Menu"
    bl_description = "Display the list of custom compositors."

    workflow_property: bpy.props.StringProperty()

    def execute(self, context):
        """Execute the operator."""

        # Store workflow property in scene properties for the menu to access
        scene = context.scene
        scene.comfyui_menu_workflow_property = self.workflow_property

        # Show the context menu
        bpy.ops.wm.call_menu(name="COMFY_MT_custom_compositor_menu")
        return {'FINISHED'}


def register():
    """Register the operator."""

    # Register scene properties for menu data
    bpy.types.Scene.comfyui_menu_workflow_property = bpy.props.StringProperty()

    bpy.utils.register_class(ComfyBlenderOperatorShowCustomCompositorMenu)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorShowCustomCompositorMenu)

    # Check if attributes exist before deleting them
    if hasattr(bpy.types.Scene, "comfyui_menu_workflow_property"):
        del bpy.types.Scene.comfyui_menu_workflow_property

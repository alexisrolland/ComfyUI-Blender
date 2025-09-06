"""Operator to display the connection menu."""
import bpy


class ComfyBlenderOperatorShowConnectionMenu(bpy.types.Operator):
    """Operator to display the connection menu."""

    bl_idname = "comfy.show_connection_menu"
    bl_label = "Show Connection Menu"
    bl_description = "Display the connection menu."

    def execute(self, context):
        """Execute the operator."""

        # Show the context menu
        bpy.ops.wm.call_menu(name="COMFY_MT_connection_menu")
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorShowConnectionMenu)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorShowConnectionMenu)

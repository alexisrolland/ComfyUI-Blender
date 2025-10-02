"""Operator to display the connection menu."""
import bpy


class ComfyBlenderOperatorShowConnectionMenu(bpy.types.Operator):
    """Operator to display the connection menu."""

    bl_idname = "comfy.show_connection_menu"
    bl_label = "Show Connection Menu"
    bl_description = "Display the connection menu."

    client_id: bpy.props.StringProperty(
        name="Client ID",
        description="Custom client ID to pass to the connection menu",
        default=""
    )

    def execute(self, context):
        """Execute the operator."""

        # Store the client_id in the scene for the menu to access it
        context.scene["comfyui_client_id"] = self.client_id

        # Show the context menu
        bpy.ops.wm.call_menu(name="COMFY_MT_connection_menu")
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorShowConnectionMenu)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorShowConnectionMenu)

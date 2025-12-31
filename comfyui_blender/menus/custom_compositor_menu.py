"""Context menu to display custom compositors for the input load image."""
import bpy


class ComfyBlenderCustomCompositorMenu(bpy.types.Menu):
    """Context menu to display custom compositors for the input load image."""

    bl_label = ""  # Hide label
    bl_idname = "COMFY_MT_custom_compositor_menu"

    def draw(self, context):
        layout = self.layout

        # Custom compositors
        layout.label(text="Custom Compositors", icon="NODE_COMPOSITING")

        # Loop over all node groups in the blend file
        for node_tree in bpy.data.node_groups:
            # Check if it's a compositor node tree
            if node_tree.type == "COMPOSITING":
                row = layout.row()
                custom_render = row.operator("comfy.render_custom_compositor", text=node_tree.name)
                custom_render.compositor_name = node_tree.name
                custom_render.workflow_property = context.scene.comfyui_menu_workflow_property


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderCustomCompositorMenu)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderCustomCompositorMenu)
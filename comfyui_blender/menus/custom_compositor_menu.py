"""Context menu to display custom compositors for the input load image."""
import bpy


class ComfyBlenderCustomCompositorMenu(bpy.types.Menu):
    """Context menu to display custom compositors for the input load image."""

    bl_label = ""  # Hide label
    bl_idname = "COMFY_MT_custom_compositor_menu"

    def draw(self, context):
        layout = self.layout

        # Check if there are any compositor node trees
        compositors = [compositor for compositor in bpy.data.node_groups if compositor.type == "COMPOSITING"]

        if not compositors:
            layout.label(text="No custom compositor found", icon="NODE_COMPOSITING")
        else:
            # Custom compositors
            layout.label(text="Custom Compositors", icon="NODE_COMPOSITING")

            # Loop over all node groups in the blend file
            for compositor in compositors:
                row = layout.row()
                custom_render = row.operator("comfy.render_custom_compositor", text=compositor.name)
                custom_render.compositor_name = compositor.name
                custom_render.workflow_property = context.scene.comfyui_menu_workflow_property


def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderCustomCompositorMenu)


def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderCustomCompositorMenu)
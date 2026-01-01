"""Panel to display mask painting features."""
import bpy


class ComfyBlenderPanelPaintMask(bpy.types.Panel):
    """Panel to display mask painting features."""

    bl_label = "Paint"
    bl_idname = "COMFY_PT_Paint"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="BRUSH_DATA")

    def draw(self, context):
        """Draw the panel."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        if addon_prefs.connection_status:
            # Select brush section
            self.layout.label(text="Select Brush:")
            box = self.layout.box()

            # Button to select the mask painting brush
            row = box.row()
            mask_brush = row.operator("comfy.select_brush", text="Mask", icon="IMAGE_RGB_ALPHA")
            mask_brush.blend_mode = "ERASE_ALPHA"
            mask_brush.custom_label = "Select the mask painting brush."

            # Button to select the mask eraser brush
            mask_brush = row.operator("comfy.select_brush", text="Eraser", icon="IMAGE_RGB")
            mask_brush.blend_mode = "ADD_ALPHA"
            mask_brush.custom_label = "Select the eraser brush."

            # Display brush size and strength control
            if context.tool_settings.image_paint.brush:
                brush = context.tool_settings.image_paint.brush
                if brush.name == "Mask Brush":
                    row = box.row()
                    row.label(text="Brush Size:")
                    row.prop(context.tool_settings.image_paint.brush, "size", text="")

                    row = box.row()
                    row.label(text="Brush Strength:")
                    row.prop(context.tool_settings.image_paint.brush, "strength", text="")

            # Add target input selection
            row = self.layout.row(align=True)
            row.label(text="Send to Input:")
            row.prop(context.scene, "comfyui_target_input", text="")
            send_input = row.operator("comfy.send_to_input", text="", icon="INDIRECT_ONLY_ON")
            send_input.name = context.edit_image.name if context.edit_image else ""
            send_input.type = "image"
            send_input.workflow_property = context.scene.comfyui_target_input

            # Button to reload the image from disk
            self.layout.operator("image.reload", text="Reset Image", icon="FILE_REFRESH")

        else:
            box = self.layout.box()
            box.label(text="Connect to the ComfyUI server to edit the image.")

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelPaintMask)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelPaintMask)

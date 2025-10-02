"""Operator to select the mask painting brush."""
import os

import bpy


class ComfyBlenderOperatorSelectMaskBrush(bpy.types.Operator):
    """Operator to select the mask painting brush."""

    bl_idname = "comfy.select_brush"
    bl_label = "Select Brush"
    bl_description = "Select custom brush."

    blend_mode: bpy.props.StringProperty(name="Blend Mode")
    custom_label: bpy.props.StringProperty(
        name="Custom Label",
        description="Custom label for the operator.",
        options={'HIDDEN'}
    )

    @classmethod
    def description(cls, context, properties):
        # Use a custom description
        custom_label = getattr(properties, "custom_label", "")
        if custom_label:
            return custom_label
        return cls.bl_description

    def execute(self, context):
        """Execute the operator."""

        context.space_data.ui_mode = "PAINT"

        brush_name = "Mask Brush"
        if brush_name not in bpy.data.brushes:
            brush = bpy.data.brushes.new(name=brush_name, mode="TEXTURE_PAINT")
        else:
            brush = bpy.data.brushes[brush_name]

        # Configure brush for mask painting
        context.scene.tool_settings.unified_paint_settings.use_unified_size = False
        context.scene.tool_settings.unified_paint_settings.use_unified_strength = False
        brush.blend = self.blend_mode
        brush.size = 50
        brush.strength = 1.0

        # Mark brush as an asset if not already marked
        if not brush.asset_data:
            brush.asset_mark()
            brush.asset_data.description = "Brush for mask painting with alpha."

            # Get icon path
            addon_folder = os.path.dirname(os.path.dirname(__file__))
            icon_path = os.path.join(addon_folder, "assets", "icon_paint_mask.png")

            # Override the context to load the custom preview
            # This is necessary because bpy.ops.ed.lib_id_load_custom_preview
            # is an operator and typically requires UI interaction or context override.
            with bpy.context.temp_override(id=brush):
                bpy.ops.ed.lib_id_load_custom_preview(filepath=icon_path)

        # Activate brush
        bpy.ops.brush.asset_activate(
            asset_library_type="LOCAL",
            asset_library_identifier="",
            relative_asset_identifier=os.path.join("Brush", f"{brush_name}")  #f"Brush\\{brush_name}" 
        )
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorSelectMaskBrush)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorSelectMaskBrush)

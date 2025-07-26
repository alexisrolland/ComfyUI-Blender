"""Operator to change the layout of the output panel."""
import bpy


class ComfyBlenderSwitchOutputLayout(bpy.types.Operator):
    """Operator to change the layout of the output panel."""

    bl_idname = "comfy.switch_output_layout"
    bl_label = "Switch Output Layout"
    bl_description = "Switch the layout of the output panel."

    layout_type: bpy.props.StringProperty(name="Layout Type")

    def execute(self, context):
        """Execute the operator."""

        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        addon_prefs.outputs_layout = self.layout_type
        return {'FINISHED'}

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderSwitchOutputLayout)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderSwitchOutputLayout)

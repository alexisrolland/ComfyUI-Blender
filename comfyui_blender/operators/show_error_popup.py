"""Operator to display an error popup window."""
import textwrap

import bpy


class ComfyBlenderOperatorShowErrorPopup(bpy.types.Operator):
    """Operator to display an error popup window."""

    bl_idname = "comfy.show_error_popup"
    bl_label = "Execution Error"
    bl_description = "Display an error popup window"

    error_message: bpy.props.StringProperty(name="Error Message")

    def execute(self, context):
        """Execute the operator."""

        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the popup window."""

        self.bl_label = "Execution Error"
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        """Customize the confirmation dialog."""

        layout = self.layout
        col = layout.column(align=True)

        # Wrap text to specified width
        wrapped_lines = textwrap.wrap(self.error_message, width=70)
        for line in wrapped_lines:
            col.label(text=line)


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorShowErrorPopup)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorShowErrorPopup)

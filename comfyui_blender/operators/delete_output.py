"""Operator to delete an output."""
import os

import bpy

from ..utils import get_outputs_folder


class ComfyBlenderOperatorDeleteOutput(bpy.types.Operator):
    """Operator to delete an output."""

    bl_idname = "comfy.delete_output"
    bl_label = "Delete Output"
    bl_description = "Delete the output from the outputs collection."

    name: bpy.props.StringProperty(name="Name")
    filepath: bpy.props.StringProperty(name="File Path")
    type: bpy.props.StringProperty(name="Type")

    def execute(self, context):
        """Execute the operator."""

        return {'FINISHED'}

    def invoke(self, context, event):
        """Show a confirmation dialog box."""

        # Use invoke popup instead invoke props dialog to avoid blocking thread
        # Invoke popup requires a custom OK / Cancel buttons
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        """Customize the confirmation dialog."""

        layout = self.layout

        # Title
        row = layout.row()
        row.label(text="Delete Output", icon="QUESTION")
        layout.separator(type="LINE")

        # Message
        col = layout.column(align=True)
        col.label(text="Are you sure you want to delete:")
        col.label(text=f"{self.name}?")

        # Buttons
        row = layout.row()
        button_ok = row.operator("comfy.delete_output_ok", text="OK", depress=True)
        button_ok.name = self.name
        button_ok.filepath = self.filepath
        button_ok.type = self.type
        row.operator("comfy.delete_output_cancel", text="Cancel")


class ComfyBlenderOperatorDeleteOutputOk(bpy.types.Operator):
    """Confirm deletion."""

    bl_idname = "comfy.delete_output_ok"
    bl_label = "Confirm Delete"
    bl_description = "Confirm the deletion of the output."
    bl_options = {'INTERNAL'}

    name: bpy.props.StringProperty(name="Name")
    filepath: bpy.props.StringProperty(name="File Path")
    type: bpy.props.StringProperty(name="Type")

    def execute(self, context):
        """Execute the operator."""

        # Remove output from Blender's data
        if self.type == "image":
            # Get the full path of the image
            outputs_folder = get_outputs_folder()
            image_filepath = os.path.join(outputs_folder, self.filepath)

            # Check if image exists in the data block and remove it
            for image in bpy.data.images:
                if image.filepath == image_filepath:
                    bpy.data.images.remove(image)
                    self.report({'INFO'}, f"Removed image from Blender data: {self.name}")
        
        elif self.type == "text":
            # Get the full path of the text object
            outputs_folder = get_outputs_folder()
            text_filepath = os.path.join(outputs_folder, self.filepath)

            # Check if text object exists in the data block and remove it
            for text in bpy.data.texts:
                if text.filepath == text_filepath:
                    bpy.data.texts.remove(text)
                    self.report({'INFO'}, f"Removed text object from Blender data: {self.name}")

        # Find and delete the output from the collection
        project_settings = bpy.context.scene.comfyui_project_settings
        outputs_collection = project_settings.outputs_collection
        for index, output in enumerate(outputs_collection):
            if output.name == self.name and output.filepath == self.filepath:
                outputs_collection.remove(index)
                self.report({'INFO'}, f"Removed output from collection: {self.name}")
        return {'FINISHED'}


class ComfyBlenderOperatorDeleteOutputCancel(bpy.types.Operator):
    """Cancel deletion."""

    bl_idname = "comfy.delete_output_cancel"
    bl_label = "Cancel Delete"
    bl_description = "Cancel the deletion of the output."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        """Execute the operator."""

        return {'CANCELLED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDeleteOutput)
    bpy.utils.register_class(ComfyBlenderOperatorDeleteOutputOk)
    bpy.utils.register_class(ComfyBlenderOperatorDeleteOutputCancel)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteOutput)
    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteOutputOk)
    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteOutputCancel)

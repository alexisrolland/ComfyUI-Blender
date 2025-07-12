"""Operator to open Blender's built-in file browser."""
import bpy


class ComfyBlenderOperatorOpenImageEditor(bpy.types.Operator):
    """Operator to open Blender's built-in image editor."""

    bl_idname = "comfy.open_image_editor"
    bl_label = "Open Image"
    bl_description = "Open the image in Blender's built-in editor"

    filename: bpy.props.StringProperty(name="File Name")

    def execute(self, context):
        """Execute the operator."""

        # Split the screen to create a new area
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.25)

        # Get the newly created area (the last one)
        area = context.screen.areas[-1]
        area.type = "IMAGE_EDITOR"

        # Access the image editor space
        space = area.spaces[0]
        space.image = bpy.data.images.get(self.filename)
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorOpenImageEditor)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorOpenImageEditor)

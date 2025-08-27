"""Operator to open Blender's image editor."""
import bpy


class ComfyBlenderOperatorOpenImageEditor(bpy.types.Operator):
    """Operator to open Blender's image editor."""

    bl_idname = "comfy.open_image_editor"
    bl_label = "Open Image"
    bl_description = "Open the image in Blender's image editor."

    name: bpy.props.StringProperty(name="Name")

    def execute(self, context):
        """Execute the operator."""

        # Check if there is already an image editor area
        image_editor_area = None
        for area in context.screen.areas:
            if area.type == "IMAGE_EDITOR":
                image_editor_area = area
                break

        # If no image editor area exists, split the screen to create one
        if image_editor_area is None:
            bpy.ops.screen.area_split(direction="VERTICAL", factor=0.5)

            # Get the newly created area (the last one)
            image_editor_area = context.screen.areas[-1]
            image_editor_area.type = "IMAGE_EDITOR"

        # Access the image editor space and set the image
        space = image_editor_area.spaces[0]
        space.image = bpy.data.images.get(self.name)
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorOpenImageEditor)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorOpenImageEditor)

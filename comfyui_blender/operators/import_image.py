"""Operator to import an image in the scene."""
import logging
import math

import bpy


log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorImportImage(bpy.types.Operator):
    """Operator to import an image in the scene."""

    bl_idname = "comfy.import_image"
    bl_label = "Import Image"
    bl_description = "Import an image in the scene."

    name: bpy.props.StringProperty(name="Name")

    def execute(self, context):
        """Execute the operator."""

        # Create an empty object and link to active region
        empty = bpy.data.objects.new(name="ImageEmpty", object_data=None)
        bpy.context.collection.objects.link(empty)

        # Set empty properties
        empty.empty_display_type = 'IMAGE'
        empty.data = bpy.data.images[self.name]
        empty.rotation_euler = (math.radians(90), 0, math.radians(45))
        empty.empty_display_size = 5
        empty.empty_image_depth = "BACK"
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportImage)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportImage)

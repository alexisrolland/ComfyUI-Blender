"""Operator to search and select an image from Blender data"""
import logging

import bpy

log = logging.getLogger("comfyui_blender")


def image_items(self, context):
    """Function to get the list of images in Blender data"""

    items = []
    for i, image in enumerate(bpy.data.images):
        # Identifier, name, description, icon, number
        items.append((image.name, image.name, getattr(image, "filepath", "") or "", "IMAGE_DATA", i))
    if not items:
        items.append(("none", "None", "No image found", "ERROR", 0))
    return items


class ComfyBlenderOperatorSearchImage(bpy.types.Operator):
    """Operator to search and select an image from Blender data"""

    bl_idname = "comfy.search_image"
    bl_label = "Search Image"
    bl_description = "Search and select an image from Blender data"
    bl_property = "image"

    # Property in which to store the selected image from the invoke_search_popup
    image: bpy.props.EnumProperty(name="Image", description="Select an image", default=None, items=image_items)
    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        if self.image == "none":
            error_message = "No image available"
            log.warning(error_message)
            return {'CANCELLED'}

        selected_image = bpy.data.images.get(self.image)
        if not selected_image:
            error_message = "Image not found"
            log.exception(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Store the selected image in the workflow property
        context.scene.current_workflow[self.workflow_property] = selected_image
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorSearchImage)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorSearchImage)

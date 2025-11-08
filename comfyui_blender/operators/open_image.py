"""Operator to load an image from disk and open it in the image editor."""
import logging

import bpy

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorImportInputImage(bpy.types.Operator):
    """Operator to load and open an image."""

    bl_idname = "comfy.open_image"
    bl_label = "Open Image"
    bl_description = "Load an image from disk and open it in the image editor."

    filepath: bpy.props.StringProperty(name="File Path", subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(name="File Filter", default="*.jpeg;*.jpg;*.png;*.webp")
    invoke_default: bpy.props.BoolProperty(default=True, options={'HIDDEN'})

    def execute(self, context):
        """Execute the operator."""

        # Load image in the data block and open it in the image editor
        if self.filepath.lower().endswith((".jpeg", ".jpg", ".png", ".webp")):
            image = bpy.data.images.load(self.filepath, check_existing=True)
            bpy.ops.comfy.open_image_editor(name=image.name)

        else:
            error_message = "Selected file is not a *.jpeg;*.jpg;*.png;*.webp."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector."""

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorImportInputImage)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorImportInputImage)

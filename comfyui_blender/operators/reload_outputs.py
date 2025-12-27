"""Operator to reload outputs."""
import os
import pathlib

import bpy

from ..utils import get_outputs_folder


class ComfyBlenderOperatorReloadOutputs(bpy.types.Operator):
    """Operator to reload outputs."""

    bl_idname = "comfy.reload_outputs"
    bl_label = "Reload Outputs"
    bl_description = "Reload outputs from the outputs folder."

    def execute(self, context):
        """Execute the operator."""

        return {'FINISHED'}
    
    def invoke(self, context, event):
        """Show a confirmation dialog box."""

        # Use invoke popup instead invoke props dialog to avoid blocking thread
        # Invoke popup requires a custom OK / Cancel buttons
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        """Customize the confirmation dialog."""

        layout = self.layout

        # Title
        row = layout.row()
        row.label(text="Reload Outputs", icon="QUESTION")
        layout.separator(type="LINE")

        # Message
        col = layout.column(align=True)
        col.label(text="Reloading outputs will delete all current outputs from the .blend file.")
        col.label(text="Are you sure you want to reload outputs?")

        # Buttons
        row = layout.row()
        row.operator("comfy.reload_outputs_ok", text="OK", depress=True)
        row.operator("comfy.reload_outputs_cancel", text="Cancel")


class ComfyBlenderOperatorReloadOutputsOk(bpy.types.Operator):
    """Cancel reload outputs."""

    bl_idname = "comfy.reload_outputs_ok"
    bl_label = "Confirm Reload"
    bl_description = "Confirm the reloading of outputs."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        """Execute the operator."""

        # Get list of files from outputs folder, including subfolders, and sort by creation date
        outputs_folder = get_outputs_folder()
        files = [f for f in pathlib.Path(outputs_folder).rglob('*') if f.is_file()]
        files = sorted(files, key=lambda f: f.stat().st_ctime)

        # Get outputs collection
        project_settings = bpy.context.scene.comfyui_project_settings
        outputs_collection = project_settings.outputs_collection

        # Delete outputs objects from Blender file if they are not used
        for output in outputs_collection:
            if output.type == "image":
                image = bpy.data.images.get(output.name)
                if image and image.users == 0:
                    bpy.data.images.remove(image)
            elif output.type == "text":
                text = bpy.data.texts.get(output.name)
                if text and text.users == 0:
                    bpy.data.texts.remove(text)

        # Clear collection before reloading
        outputs_collection.clear()

        # Loop over files
        for f in files:
            relative_path = f.relative_to(outputs_folder)

            # 3D model file
            if f.suffix.lower() in (".glb", ".gltf", ".obj"):
                output = outputs_collection.add()
                output.name = f.name
                output.filepath = str(relative_path)
                output.type = "3d"

            # Image file
            elif f.suffix.lower() in (".jpeg", ".jpg", ".png", ".webp"):
                # Load image into Blender file to get the name
                image = bpy.data.images.load(str(f), check_existing=True)
                image.preview_ensure()

                # Add image to outputs collection
                output = outputs_collection.add()
                output.name = image.name
                output.filepath = str(relative_path)
                output.type = "image"

            # Text file
            elif f.suffix.lower() in (".txt"):
                # Load text into Blender file to get the name
                text = bpy.data.texts.load(str(f))

                # Add text to outputs collection
                output = outputs_collection.add()
                output.name = text.name
                output.filepath = str(relative_path)
                output.type = "text"

            else:
                self.report({'WARNING'}, f"Unsupported file type for output: {str(f)}")

        # Force redraw of the UI
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type in ("VIEW_3D", "IMAGE_EDITOR"):
                    area.tag_redraw()

        self.report({'INFO'}, f"Outputs reloaded from folder: {outputs_folder}")
        return {'FINISHED'}


class ComfyBlenderOperatorReloadOutputsCancel(bpy.types.Operator):
    """Cancel reload outputs."""

    bl_idname = "comfy.reload_outputs_cancel"
    bl_label = "Cancel Reload"
    bl_description = "Cancel the reloading of outputs."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        """Execute the operator."""

        return {'CANCELLED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorReloadOutputs)
    bpy.utils.register_class(ComfyBlenderOperatorReloadOutputsOk)
    bpy.utils.register_class(ComfyBlenderOperatorReloadOutputsCancel)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorReloadOutputs)
    bpy.utils.unregister_class(ComfyBlenderOperatorReloadOutputsOk)
    bpy.utils.unregister_class(ComfyBlenderOperatorReloadOutputsCancel)

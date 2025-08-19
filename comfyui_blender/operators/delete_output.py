"""Operator to delete an output."""
import bpy


class ComfyBlenderOperatorDeleteOutput(bpy.types.Operator):
    """Operator to delete an output."""

    bl_idname = "comfy.delete_output"
    bl_label = "Delete Output"
    bl_description = "Delete the output from the outputs collection."

    filename: bpy.props.StringProperty(name="File Name")
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
        row.label(text="Delete Output")
        layout.separator(type="LINE")

        # Message
        col = layout.column(align=True)
        col.label(text="Are you sure you want to delete:")
        col.label(text=f"{self.filename}?")

        # Buttons
        row = layout.row()
        button_ok = row.operator("comfy.delete_output_ok", text="OK", depress=True)
        button_ok.filename = self.filename
        button_ok.filepath = self.filepath
        button_ok.type = self.type
        row.operator("comfy.delete_output_cancel", text="Cancel")


class ComfyBlenderOperatorDeleteOutputOk(bpy.types.Operator):
    """Confirm deletion."""

    bl_idname = "comfy.delete_output_ok"
    bl_label = "Confirm Delete"
    bl_description = "Confirm the deletion of the output."
    bl_options = {'INTERNAL'}

    filename: bpy.props.StringProperty(name="File Name")
    filepath: bpy.props.StringProperty(name="File Path")
    type: bpy.props.StringProperty(name="Type")

    def execute(self, context):
        """Execute the operator."""

        # Get outputs collection
        project_settings = bpy.context.scene.comfyui_project_settings
        outputs_collection = project_settings.outputs_collection

        # Find and delete the output from the collection
        outputs_collection.remove(outputs_collection.find(self.filepath))
        self.report({'INFO'}, f"Removed output from collection: {self.filename}")

        # Remove output from Blender's data
        if self.type == "image":
            image = bpy.data.images.get(self.filename)
            bpy.data.images.remove(image)
            self.report({'INFO'}, f"Removed image from Blender data: {self.filename}")
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

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

        # Get outputs collection
        addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
        outputs_collection = addon_prefs.outputs_collection

        # Find and delete the item with the matching property value
        for index, output in enumerate(outputs_collection):
            if output.filepath == self.filepath:
                outputs_collection.remove(index)
                self.report({'INFO'}, f"Deleted output from collection, file path: {self.filepath}")

        # Remove the output from Blender's data
        if self.type == "image":
            image = bpy.data.images.get(self.filename)
            bpy.data.images.remove(image)
            self.report({'INFO'}, f"Deleted output from Blender data, file name: {self.filename}")
        return {'FINISHED'}

    def invoke(self, context, event):
        """Show a confirmation dialog box."""

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        """Customize the confirmation dialog."""

        layout = self.layout
        col = layout.column(align=True)
        col.label(text=f"Are you sure you want to delete:")
        col.label(text=f"{self.filename}?")

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDeleteOutput)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteOutput)

"""Operator to delete an input."""
import bpy


class ComfyBlenderOperatorDeleteInput(bpy.types.Operator):
    """Operator to delete an input."""

    bl_idname = "comfy.delete_input"
    bl_label = "Delete Input"
    bl_description = "Delete the input from the workflow."

    filename: bpy.props.StringProperty(name="File Name")
    workflow_property: bpy.props.StringProperty(name="Workflow Property")
    type: bpy.props.StringProperty(name="Type")

    def execute(self, context):
        """Execute the operator."""

        # Remove input file path from workflow
        context.scene.current_workflow[self.workflow_property] = None
        self.report({'INFO'}, f"Removed input from workflow")

        # Remove input from Blender's data
        if self.type == "image":
            image = bpy.data.images.get(self.filename)
            bpy.data.images.remove(image)
            self.report({'INFO'}, f"Removed image from Blender data: {self.filename}")
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

    bpy.utils.register_class(ComfyBlenderOperatorDeleteInput)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteInput)

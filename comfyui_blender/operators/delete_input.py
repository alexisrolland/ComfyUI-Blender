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
        row.label(text="Delete Input")
        layout.separator(type="LINE")

        # Message
        col = layout.column(align=True)
        col.label(text="Are you sure you want to delete:")
        col.label(text=f"{self.filename}?")

        # Buttons
        row = layout.row()
        button_ok = row.operator("comfy.delete_input_ok", text="OK", depress=True)
        button_ok.filename = self.filename
        button_ok.workflow_property = self.workflow_property
        button_ok.type = self.type
        row.operator("comfy.delete_input_cancel", text="Cancel")

class ComfyBlenderOperatorDeleteInputOk(bpy.types.Operator):
    """Confirm deletion."""

    bl_idname = "comfy.delete_input_ok"
    bl_label = "Confirm Delete"
    bl_description = "Confirm the deletion of the input."
    bl_options = {'INTERNAL'}

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

class ComfyBlenderOperatorDeleteInputCancel(bpy.types.Operator):
    """Cancel deletion."""

    bl_idname = "comfy.delete_input_cancel"
    bl_label = "Cancel Delete"
    bl_description = "Cancel the deletion of the input."
    bl_options = {'INTERNAL'}

    def execute(self, context):
        """Execute the operator."""

        return {'CANCELLED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorDeleteInput)
    bpy.utils.register_class(ComfyBlenderOperatorDeleteInputOk)
    bpy.utils.register_class(ComfyBlenderOperatorDeleteInputCancel)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteInput)
    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteInputOk)
    bpy.utils.unregister_class(ComfyBlenderOperatorDeleteInputCancel)

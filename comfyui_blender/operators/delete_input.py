"""Operator to delete an input."""
import bpy

from ..workflow import get_current_workflow_inputs


class ComfyBlenderOperatorDeleteInput(bpy.types.Operator):
    """Operator to delete an input."""

    bl_idname = "comfy.delete_input"
    bl_label = "Delete Input"
    bl_description = "Delete the input from the workflow."

    name: bpy.props.StringProperty(name="Name")
    filepath: bpy.props.StringProperty(name="File Path")
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
        row.label(text="Delete Input", icon="QUESTION")
        layout.separator(type="LINE")

        # Message
        col = layout.column(align=True)
        col.label(text="Are you sure you want to delete:")
        col.label(text=f"{self.name}?")

        # Buttons
        row = layout.row()
        button_ok = row.operator("comfy.delete_input_ok", text="OK", depress=True)
        button_ok.name = self.name
        button_ok.filepath = self.filepath
        button_ok.workflow_property = self.workflow_property
        button_ok.type = self.type
        row.operator("comfy.delete_input_cancel", text="Cancel")


class ComfyBlenderOperatorDeleteInputOk(bpy.types.Operator):
    """Confirm deletion."""

    bl_idname = "comfy.delete_input_ok"
    bl_label = "Confirm Delete"
    bl_description = "Confirm the deletion of the input."
    bl_options = {'INTERNAL'}

    name: bpy.props.StringProperty(name="File Name")
    filepath: bpy.props.StringProperty(name="File Path")
    workflow_property: bpy.props.StringProperty(name="Workflow Property")
    type: bpy.props.StringProperty(name="Type")

    def execute(self, context):
        """Execute the operator."""

        # Get current workflow
        current_workflow = context.scene.current_workflow

        if self.type == "image":
            # Delete the input image from Blender's data
            # Only if the image is not used in any of the workflow inputs
            image = getattr(current_workflow, self.workflow_property)
            possible_inputs = get_current_workflow_inputs(self, context, ("BlenderInputLoadImage", "BlenderInputLoadMask"))
            is_used = False  # Flag to check if the image is used in any other input
            for input in possible_inputs:
                if input[0] != self.workflow_property:
                    if getattr(current_workflow, input[0]) == image:
                        is_used = True
                        break
            if not is_used:
                bpy.data.images.remove(image)
            else:
                setattr(current_workflow, self.workflow_property, None)

            # Delete image file
            # Do not delete file in case it is reused when reloading workflows
            # if os.path.exists(self.filepath):
            #     os.remove(self.filepath)
            #     self.report({'INFO'}, f"Deleted file: {self.filepath}")

        if self.type == "3d":
            setattr(current_workflow, self.workflow_property, "")

            # Delete 3D model file
            # Do not delete file in case it is reused when reloading workflows
            # if os.path.exists(self.filepath):
            #     os.remove(self.filepath)
            #     self.report({'INFO'}, f"Deleted file: {self.filepath}")

        if self.type == "text":
            # Delete the input text from Blender's data
            # Only if the text is not used in any of the workflow inputs
            text = getattr(current_workflow, self.workflow_property)
            possible_inputs = get_current_workflow_inputs(self, context, ("BlenderInputStringMultiline"))
            is_used = False  # Flag to check if the text is used in any other input
            for input in possible_inputs:
                if input[0] != self.workflow_property:
                    if getattr(current_workflow, input[0]) == text:
                        is_used = True
                        break
            if not is_used:
                bpy.data.texts.remove(text)
            else:
                setattr(current_workflow, self.workflow_property, None)

        # Force redraw of the UI
        for screen in bpy.data.screens:  # Iterate through all screens
            for area in screen.areas:  # Access areas in each screen
                if area.type == "VIEW_3D":  # Area of the add-on panel
                    area.tag_redraw()

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

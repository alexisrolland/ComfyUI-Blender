"""Operator to open Blender's text editor."""
import bpy


class ComfyBlenderOperatorOpenTextEditor(bpy.types.Operator):
    """Operator to open Blender's text editor."""

    bl_idname = "comfy.open_text_editor"
    bl_label = "Edit Text"
    bl_description = "Edit text in Blender's text editor."

    name: bpy.props.StringProperty(name="Name")
    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

        # Check if there is already a text editor area
        text_editor_area = None
        for area in context.screen.areas:
            if area.type == "TEXT_EDITOR":
                text_editor_area = area
                break

        # If no text editor area exists, split the screen to create one
        if text_editor_area is None:
            bpy.ops.screen.area_split(direction="VERTICAL", factor=0.5)

            # Get the newly created area (the last one)
            text_editor_area = context.screen.areas[-1]
            text_editor_area.type = "TEXT_EDITOR"

        # Access the text editor space
        space = text_editor_area.spaces[0]
        space.show_word_wrap = True
        space.show_syntax_highlight = False

        # Select text object or create a new one if it doesn't exist
        current_workflow = context.scene.current_workflow
        text = getattr(current_workflow, self.workflow_property)
        if text:
            space.text = text
        else:
            space.text = bpy.data.texts.new("Prompt")
            setattr(current_workflow, self.workflow_property, space.text)
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorOpenTextEditor)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorOpenTextEditor)

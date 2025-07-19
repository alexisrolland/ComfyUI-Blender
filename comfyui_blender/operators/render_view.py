"""Operator to render from the camera view."""
import os

import bpy

from ..utils import get_filepath


class ComfyBlenderOperatorRenderDepthMap(bpy.types.Operator):
    """Operator to render from the camera view."""

    bl_idname = "comfy.render_view"
    bl_label = "Render View"
    bl_description = "Render from the camera."

    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

        # Create a new node tree for compositing
        tree = bpy.context.scene.node_tree
        tree.nodes.clear()

        # Create nodes
        rlayers_node = tree.nodes.new(type="CompositorNodeRLayers")
        output_file_node = tree.nodes.new(type="CompositorNodeOutputFile")

        # Link nodes
        tree.links.new(rlayers_node.outputs["Image"], output_file_node.inputs["Image"])

        # Set path to inputs folder
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        inputs_folder = str(addon_prefs.inputs_folder)
        output_file_node.base_path = inputs_folder

        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        temp_filepath = os.path.join(inputs_folder, "Image0001.png")
        render_filename, render_filepath = get_filepath("render.png", inputs_folder)
        os.rename(temp_filepath, render_filepath)
        self.report({'INFO'}, f"Render saved: {render_filepath}")

        # Load image in the data block
        bpy.data.images.load(render_filepath, check_existing=True)

        # Delete the previous input file from Blender's data if it exists
        current_workflow = context.scene.current_workflow
        previous_input_filepath = getattr(current_workflow, self.workflow_property)
        previous_input_filename = os.path.basename(previous_input_filepath)
        if bpy.data.images.get(previous_input_filename):
            image = bpy.data.images.get(previous_input_filename)
            bpy.data.images.remove(image)

        # Update the workflow property with the new input filepath
        current_workflow[self.workflow_property] = render_filepath

        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRenderDepthMap)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRenderDepthMap)

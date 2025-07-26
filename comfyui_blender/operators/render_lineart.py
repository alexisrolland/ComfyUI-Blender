"""Operator to render a lineart."""
import os
import shutil
from mathutils import Vector

import bpy

from ..utils import get_filepath, show_error_popup


class ComfyBlenderOperatorRenderLineart(bpy.types.Operator):
    """Operator to render a lineart."""

    bl_idname = "comfy.render_lineart"
    bl_label = "Render Lineart"
    bl_description = "Render a lineart from the camera."

    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

        scene = context.scene
        if not context.scene.camera:
            error_message = "No camera found"
            show_error_popup(error_message)
            return {'CANCELLED'}
        
        # Calculate position behind the camera
        camera_location = scene.camera.location.copy()
        camera_backward = scene.camera.matrix_world.to_quaternion() @ Vector((0, 0, 1))  # Camera's backward direction
        gpencil_location = camera_location + camera_backward * 5  # 5 units behind camera

        # Add a new grease pencil object
        bpy.ops.object.grease_pencil_add(type="STROKE", radius=1, align="WORLD", location=gpencil_location, scale=(1, 1, 1))

        # Assign white material to the grease pencil object
        white_material = bpy.data.materials["White"]
        gpencil = context.object
        gpencil.data.materials[0] = white_material

        # Add Lineart modifier
        bpy.ops.object.modifier_add(type="LINEART")
        lineart_modifier = context.object.modifiers["Lineart"]
        lineart_modifier.source_type = "SCENE"
        lineart_modifier.target_layer = "Color"
        lineart_modifier.target_material = white_material
        lineart_modifier.thickness = 10

        # Store original render settings
        scene = context.scene
        original_filepath = scene.render.filepath
        original_file_format = scene.render.image_settings.file_format
        original_color_mode = scene.render.image_settings.color_mode
        original_color_depth = scene.render.image_settings.color_depth
        original_compression = scene.render.image_settings.compression
        original_display_device = scene.display_settings.display_device
        original_view_transform = scene.view_settings.view_transform

        # Bake the lineart modifier to generate the strokes
        bpy.context.view_layer.objects.active = gpencil
        bpy.ops.object.lineart_bake_strokes()

        # Hide all objects except grease pencil to isolate lineart
        hidden_objects = []
        for obj in scene.objects:
            if obj != gpencil and not obj.hide_render:
                obj.hide_render = True
                hidden_objects.append(obj)

        # Set up the scene for rendering
        scene.render.filepath = os.devnull  # Disable default render output
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGB"
        scene.render.image_settings.color_depth = "16"
        scene.render.image_settings.compression = 0
        scene.display_settings.display_device = "Display P3"
        scene.view_settings.view_transform = "Raw"
        scene.render.film_transparent = True  # Enable transparent background

        # Get path to inputs folder
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        inputs_folder = str(addon_prefs.inputs_folder)
        os.makedirs(inputs_folder, exist_ok=True)

        # Create a new node tree for compositing
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        # Create nodes
        rgb_node = tree.nodes.new(type="CompositorNodeRGB")  # Create a black background
        rgb_node.outputs[0].default_value = (0, 0, 0, 1)  # Black color
        rlayers_node = tree.nodes.new(type="CompositorNodeRLayers")
        alpha_over_node = tree.nodes.new(type="CompositorNodeAlphaOver")
        output_file_node = tree.nodes.new(type="CompositorNodeOutputFile")
        output_file_node.base_path = inputs_folder

        # Connect nodes: black background as base, lineart as overlay
        tree.links.new(rgb_node.outputs["RGBA"], alpha_over_node.inputs[1])  # Background
        tree.links.new(rlayers_node.outputs["Image"], alpha_over_node.inputs[2])  # Foreground (lineart)
        tree.links.new(alpha_over_node.outputs["Image"], output_file_node.inputs["Image"])

        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        temp_filepath = os.path.join(inputs_folder, "Image0001.png")
        lineart_filename, lineart_filepath = get_filepath("lineart.png", inputs_folder)
        shutil.move(temp_filepath, lineart_filepath)  # Use shutil.move to rename file with overwrite
        self.report({'INFO'}, f"Lineart saved: {lineart_filepath}")

        # Load image in the data block
        bpy.data.images.load(lineart_filepath, check_existing=True)

        # Delete the previous input image from Blender's data
        current_workflow = context.scene.current_workflow
        previous_input_filepath = getattr(current_workflow, self.workflow_property)
        previous_input_filename = os.path.basename(previous_input_filepath)
        if bpy.data.images.get(previous_input_filename):
            image = bpy.data.images.get(previous_input_filename)
            bpy.data.images.remove(image)

        # Delete the previous input file
        if os.path.exists(previous_input_filepath):
            os.remove(previous_input_filepath)

        # Update the workflow property with the new input filepath
        current_workflow[self.workflow_property] = lineart_filepath

        # Delete grease pencil object
        bpy.data.objects.remove(gpencil, do_unlink=True)

        # Restore visibility of hidden objects
        for obj in hidden_objects:
            obj.hide_render = False

        # Restore original render settings
        scene.render.filepath = original_filepath
        scene.render.image_settings.file_format = original_file_format
        scene.render.image_settings.color_mode = original_color_mode
        scene.render.image_settings.color_depth = original_color_depth
        scene.render.image_settings.compression = original_compression
        scene.display_settings.display_device = original_display_device
        scene.view_settings.view_transform = original_view_transform
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorRenderLineart)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorRenderLineart)

"""Operator to prepare a 3D model file to import it on ComfyUI server."""
import os
import shutil
from mathutils import Vector

import bpy

from ..utils import get_filepath, show_error_popup


class ComfyBlenderOperatorPrepare3DModel(bpy.types.Operator):
    """Operator to prepare a 3D model file to import it on ComfyUI server."""

    bl_idname = "comfy.prepare_3d_model"
    bl_label = "Prepare 3D Model"
    bl_description = "Prepare a 3D model file to import it on ComfyUI server"

    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""

         # Set path to inputs folder
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        inputs_folder = str(addon_prefs.inputs_folder)
        os.makedirs(inputs_folder, exist_ok=True)
        file_name, filepath = get_filepath("3d_model.obj", inputs_folder)

        # Check if any mesh object is selected
        selected_meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]
        if not selected_meshes:
            error_message = f"Select at least one mesh object."
            show_error_popup(error_message)
            return {'CANCELLED'}

        # Export only selected objects
        bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True, export_materials=False)

        # Store original render settings
        scene = context.scene
        original_filepath = scene.render.filepath
        original_camera = scene.camera
        original_resolution_x = scene.render.resolution_x
        original_resolution_y = scene.render.resolution_y
        original_filepath = scene.render.filepath
        original_file_format = scene.render.image_settings.file_format

        # Calculate bounding box of selected meshes
        bbox_min = Vector((float('inf'), float('inf'), float('inf')))
        bbox_max = Vector((float('-inf'), float('-inf'), float('-inf')))
        
        for obj in selected_meshes:
            # Get world matrix transformed bounding box
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            for corner in bbox_corners:
                bbox_min.x = min(bbox_min.x, corner.x)
                bbox_min.y = min(bbox_min.y, corner.y)
                bbox_min.z = min(bbox_min.z, corner.z)
                bbox_max.x = max(bbox_max.x, corner.x)
                bbox_max.y = max(bbox_max.y, corner.y)
                bbox_max.z = max(bbox_max.z, corner.z)

        # Calculate center and size of bounding box
        bbox_center = (bbox_min + bbox_max) / 2
        bbox_size = bbox_max - bbox_min
        max_dimension = max(bbox_size.x, bbox_size.y, bbox_size.z)

        # Create temporary camera
        bpy.ops.object.camera_add()
        temp_camera = context.active_object
        temp_camera.name = "temp_camera"

        # Position camera to frame the objects
        # Place camera at a distance that frames the objects nicely
        camera_distance = max_dimension * 1.5
        temp_camera.location = bbox_center + Vector((camera_distance, -camera_distance, camera_distance * 0.5))
        
        # Point camera at the center of the objects
        direction = bbox_center - temp_camera.location
        temp_camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

        # Set temporary camera as active camera
        scene.camera = temp_camera

        # Set render settings for preview
        scene.render.filepath = os.devnull  # Disable default render output
        scene.render.resolution_x = 512
        scene.render.resolution_y = 512

        # Create a new node tree for compositing
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        # Create nodes
        rlayers_node = tree.nodes.new(type="CompositorNodeRLayers")
        output_file_node = tree.nodes.new(type="CompositorNodeOutputFile")
        tree.links.new(rlayers_node.outputs["Image"], output_file_node.inputs["Image"])
        output_file_node.base_path = inputs_folder

        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        temp_filepath = os.path.join(inputs_folder, "Image0001.png")
        render_filepath = filepath.replace(".obj", "_preview.png")
        shutil.move(temp_filepath, render_filepath)  # Use shutil.move to rename file with overwrite
        self.report({'INFO'}, f"Render saved: {render_filepath}")

        # Load image in the data block
        bpy.data.images.load(render_filepath, check_existing=True)

        # Delete the previous input file
        current_workflow = context.scene.current_workflow
        previous_input_filepath = getattr(current_workflow, self.workflow_property)
        if os.path.exists(previous_input_filepath):
            os.remove(previous_input_filepath)

        # Delete the previous input preview image from Blender's data
        previous_input_preview_filepath = previous_input_filepath.replace(".obj", "_preview.png")
        previous_input_preview_filename = os.path.basename(previous_input_preview_filepath)
        if bpy.data.images.get(previous_input_preview_filename):
            image = bpy.data.images.get(previous_input_preview_filename)
            bpy.data.images.remove(image)

        # Delete the previous input preview file
        if os.path.exists(previous_input_preview_filepath):
            os.remove(previous_input_preview_filepath)

        # Update the workflow property with the new input filepath
        current_workflow[self.workflow_property] = filepath

        # Clean up: Delete temporary camera
        bpy.data.objects.remove(temp_camera, do_unlink=True)
        
        # Restore original render settings
        scene.render.filepath = original_filepath
        scene.camera = original_camera
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.render.filepath = original_filepath
        scene.render.image_settings.file_format = original_file_format
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorPrepare3DModel)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorPrepare3DModel)

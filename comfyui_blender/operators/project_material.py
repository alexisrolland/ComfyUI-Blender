"""Operator to project an image as material on a mesh."""
import logging
import math

import bpy

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorProjectMaterial(bpy.types.Operator):
    """Operator to project an image as material on a mesh."""

    bl_idname = "comfy.project_material"
    bl_label = "Project as Material"
    bl_description = "Project the image on the selected mesh."

    name: bpy.props.StringProperty(name="Name")

    def execute(self, context):
        """Execute the operator."""

        # Check if a mesh object is selected
        selected_meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]
        if not selected_meshes:
            error_message = f"Select at least one mesh object."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}
        
        # Check if the scene has a camera
        camera = context.scene.camera
        if not camera:
            error_message = f"The scene should have at least one camera."
            log.error(error_message)
            bpy.ops.comfy.show_error_popup("INVOKE_DEFAULT", error_message=error_message)
            return {'CANCELLED'}

        # Create a new material with the image texture
        material = bpy.data.materials.new(name="ProjectedMaterial")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()  # Clear default nodes

        # Create nodes
        texture = nodes.new(type="ShaderNodeTexImage")
        output = nodes.new(type="ShaderNodeOutputMaterial")

        # Get image to use as texture
        image = bpy.data.images.get(self.name)
        texture.image = image

        # Link nodes
        links.new(texture.outputs["Color"], output.inputs["Surface"])

        # Loop on each selected mesh
        for obj in selected_meshes:
            # Assign material to the mesh
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)

            # Add a modifier to project the texture
            modifier = obj.modifiers.get("ProjectedMaterial")
            if modifier is None or modifier.type != "UV_PROJECT":
                modifier = obj.modifiers.new(name="ProjectedMaterial", type="UV_PROJECT")
            modifier.projector_count = 1
            modifier.projectors[0].object = camera

            # Set aspect ratio based on image dimensions
            width, height = image.size
            gcd = math.gcd(width, height)  # Greatest common divisor
            modifier.aspect_x = width // gcd
            modifier.aspect_y = height // gcd

        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorProjectMaterial)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorProjectMaterial)

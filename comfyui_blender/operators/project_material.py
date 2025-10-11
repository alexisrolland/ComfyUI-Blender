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

        # Create new geometry nodes to manage the projection
        # geometry_nodes = bpy.data.node_groups.new(name="Projection Geometry Nodes", type="GeometryNodeTree")

        # Set up the group inputs and outputs
        # geometry_nodes.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        # geometry_nodes.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

        # Get nodes and links for easier access
        # nodes = geometry_nodes.nodes
        # links = geometry_nodes.links

        # Create input and output nodes
        # input_node = nodes.new(type="NodeGroupInput")
        # output_node = nodes.new(type="NodeGroupOutput")
        # links.new(input_node.outputs[0], output_node.inputs[0])  # From output socket Geometry to input socket Geometry

        # Position the nodes
        # input_node.location = (-200, 0)
        # output_node.location = (200, 0)

        # Create a new material with the image texture
        material = bpy.data.materials.new(name="Material.Projection")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()  # Clear default nodes

        # Create shader nodes
        uv_node = nodes.new(type="ShaderNodeUVMap")
        image_node = nodes.new(type="ShaderNodeTexImage")
        output_node = nodes.new(type="ShaderNodeOutputMaterial")

        # Position shader nodes
        uv_node.location = (-200, 0)
        image_node.location = (0, 0)
        output_node.location = (300, 0)

        # Link shader nodes
        links.new(uv_node.outputs[0], image_node.inputs[0])  # From output socket Color to input socket Surface
        links.new(image_node.outputs[0], output_node.inputs[0])  # From output socket Color to input socket Surface

        # Get image and assign it to the shader texture node
        image = bpy.data.images.get(self.name)
        image_node.image = image

        # Loop on each selected mesh
        for obj in selected_meshes:
            # Select object as active
            # This id needed to make the object data single-user
            # This is needed for applying the modifier later
            context.view_layer.objects.active = obj
            obj.select_set(True)

            # Ensure the object mesh data is not used by other objects
            # obj.data = obj.data.copy() if obj.data.users > 1 else obj.data
            bpy.ops.object.make_single_user(object=True, obdata=True)

            # Assign material to the mesh
            obj.data.materials[0] = material if obj.data.materials else obj.data.materials.append(material)

            # Create new UV map for the projection
            uv_map = obj.data.uv_layers.new(name="UVMap.Projection")
            uv_map.active_render = True

            # Assign UV map to the shader UV node
            uv_node.uv_map = uv_map.name

            # Add modifier to apply the geometry nodes
            # modifier = obj.modifiers.new(name="Projected Geometry Nodes", type="NODES")
            # modifier.node_group = geometry_nodes

            # Add modifier to project the texture
            modifier = obj.modifiers.new(name="Modifier.Projection", type="UV_PROJECT")
            modifier.uv_layer = uv_map.name
            modifier.projector_count = 1
            modifier.projectors[0].object = camera

            # Set aspect ratio based on image dimensions
            width, height = image.size
            gcd = math.gcd(width, height)  # Greatest common divisor
            modifier.aspect_x = width // gcd
            modifier.aspect_y = height // gcd

            # Apply the modifier
            bpy.ops.object.modifier_apply(modifier=modifier.name)

        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorProjectMaterial)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorProjectMaterial)

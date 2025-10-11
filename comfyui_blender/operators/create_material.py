"""Operator to use an image as material on a mesh."""
import logging

import bpy

log = logging.getLogger("comfyui_blender")


class ComfyBlenderOperatorCreateMaterial(bpy.types.Operator):
    """Operator to use an image as material on a mesh."""

    bl_idname = "comfy.create_material"
    bl_label = "Create Material"
    bl_description = "Use the image as material for the selected mesh."

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

        # Create a new material
        material = bpy.data.materials.new(name="Material")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()  # Clear default nodes

        # Create shader nodes
        coordinates_node = nodes.new(type="ShaderNodeTexCoord")
        mapping_node = nodes.new(type="ShaderNodeMapping")
        basecolor_node = nodes.new(type="ShaderNodeTexImage")
        metallic_node = nodes.new(type="ShaderNodeTexImage")
        roughness_node = nodes.new(type="ShaderNodeTexImage")
        normal_node = nodes.new(type="ShaderNodeTexImage")
        normal_map_node = nodes.new(type="ShaderNodeNormalMap")
        bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
        output_node = nodes.new(type="ShaderNodeOutputMaterial")

        # Label nodes
        basecolor_node.label = "Base Color"
        metallic_node.label = "Metallic"
        roughness_node.label = "Roughness"
        normal_node.label = "Normal"

        # Position shader nodes
        coordinates_node.location = (-500, 0)
        mapping_node.location = (-300, 0)
        basecolor_node.location = (0, 300)
        metallic_node.location = (0, 0)
        roughness_node.location = (0, -300)
        normal_node.location = (0, -600)
        normal_map_node.location = (300, -600)
        bsdf_node.location = (500, 0)
        output_node.location = (800, 0)

        # Link shader nodes
        links.new(coordinates_node.outputs[2], mapping_node.inputs[0])  # From output socket UV to input socket Vector
        links.new(mapping_node.outputs[0], basecolor_node.inputs[0])  # From output socket Vector to input socket Vector
        links.new(mapping_node.outputs[0], metallic_node.inputs[0])  # From output socket Vector to input socket Vector
        links.new(mapping_node.outputs[0], roughness_node.inputs[0])  # From output socket Vector to input socket Vector
        links.new(mapping_node.outputs[0], normal_node.inputs[0])  # From output socket Vector to input socket Vector
        links.new(basecolor_node.outputs[0], bsdf_node.inputs[0])  # From output socket Color to input socket Base Color
        links.new(normal_node.outputs[0], normal_map_node.inputs[1])  # From output socket Color to input socket Color
        links.new(bsdf_node.outputs[0], output_node.inputs[0])  # From output socket BSDF to input socket Surface

        # Do not connect by default because this impacts the appearance
        # links.new(metallic_node.outputs[0], bsdf_node.inputs[1])  # From output socket Color to input socket Base Metallic
        # links.new(roughness_node.outputs[0], bsdf_node.inputs[2])  # From output socket Color to input socket Roughness
        # links.new(normal_map_node.outputs[0], bsdf_node.inputs[5])  # From output socket Normal to input socket Normal

        # Get image and assign it to the basecolor node
        image = bpy.data.images.get(self.name)
        basecolor_node.image = image

        # Add note
        note_node = nodes.new(type="NodeFrame")
        note_node.label = "Connect the image nodes you need."
        note_node.width = 400
        note_node.height = 50
        note_node.location = (430, -400)

        # Loop on each selected mesh
        for obj in selected_meshes:
            # Assign material to the mesh
            obj.data.materials[0] = material if obj.data.materials else obj.data.materials.append(material)

        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorCreateMaterial)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorCreateMaterial)

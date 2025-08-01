"""Operator to get the camera width or height."""
import bpy


class ComfyBlenderOperatorGetCameraResolution(bpy.types.Operator):
    """Operator to get the camera width or height."""

    bl_idname = "comfy.get_camera_resolution"
    bl_label = "Get Camera Resolution"
    bl_description = "Update the input value with the camera resolution."

    property_name: bpy.props.StringProperty(name="Property Name")
    axis: bpy.props.EnumProperty(name="Axis", items=[("X", "X Axis", "Get the camera resolution width"), ('Y', "Y Axis", "Get the camera resolution height")])

    def execute(self, context):
        """Execute the operator."""

        if self.axis == "X":
            context.scene.current_workflow[self.property_name] = context.scene.render.resolution_x
        elif self.axis == "Y":
            context.scene.current_workflow[self.property_name] = context.scene.render.resolution_y
        return {'FINISHED'}

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorGetCameraResolution)

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorGetCameraResolution)

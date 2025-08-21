"""Operator to set the camera width or height."""
import bpy


class ComfyBlenderOperatorSetCameraResolution(bpy.types.Operator):
    """Operator to set the camera width or height."""

    bl_idname = "comfy.set_camera_resolution"
    bl_label = "Set Camera Resolution"
    bl_description = "Update the camera resolution with the input value."

    value: bpy.props.IntProperty(name="Camera Resolution")
    axis: bpy.props.EnumProperty(name="Axis", items=[("X", "X Axis", "Set the camera resolution width"), ('Y', "Y Axis", "Set the camera resolution height")])

    def execute(self, context):
        """Execute the operator."""

        if self.axis == "X":
            context.scene.render.resolution_x = self.value
        elif self.axis == "Y":
            context.scene.render.resolution_y = self.value
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorSetCameraResolution)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorSetCameraResolution)

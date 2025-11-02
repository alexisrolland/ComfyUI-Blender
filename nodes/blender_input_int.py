from comfy_api.latest import io
from comfy_extras.nodes_primitive import Int
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_MIN,
    TOOLTIP_MAX,
    TOOLTIP_ORDER,
    TOOLTIP_STEP
)


class BlenderInputInt(Int):
    """Display an integer input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputInt"
        schema.display_name="Blender Input Integer"
        schema.description="Display an integer input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.Int.Input("default", default=0, tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Int.Input("min", default=MIN_INT, min=MIN_INT, max=MAX_INT, step=1, tooltip=TOOLTIP_MIN))
        schema.inputs.append(io.Int.Input("max", default=MAX_INT, min=MIN_INT, max=MAX_INT, step=1, tooltip=TOOLTIP_MAX))
        schema.inputs.append(io.Int.Input("step", default=1, min=1, max=MAX_INT, step=1, tooltip=TOOLTIP_STEP))
        schema.inputs.append(io.Boolean.Input("camera_width", default=False, tooltip="Display a button to set/get the camera width."))
        schema.inputs.append(io.Boolean.Input("camera_height", default=False, tooltip="Display a button to set/get the camera height."))

        # Overwrite value input to remove control_after_generate and overwrite min/max/step
        for i, input in enumerate(schema.inputs):
            if input.id == "value":
                schema.inputs[i] = io.Int.Input("value", default=0, min=MIN_INT, max=MAX_INT, step=1, control_after_generate=False)
                break
        return schema

    @classmethod
    def execute(cls, value: int, order: int, default: int, min: int, max: int, step: int, camera_width: bool, camera_height: bool, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(value)
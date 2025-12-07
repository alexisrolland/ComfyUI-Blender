from comfy_api.latest import io
from comfy_extras.nodes_primitive import Float
from .utils import (
    MAX_FLOAT,
    MAX_INT,
    MIN_FLOAT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_MIN,
    TOOLTIP_MAX,
    TOOLTIP_ORDER
)


class BlenderInputFloat(Float):
    """Display a float input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputFloat"
        schema.display_name="Blender Input Float"
        schema.description="Display a float input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.Float.Input("default", default=0.0, min=MIN_FLOAT, max=MAX_FLOAT, step=0.01, tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Float.Input("min", default=MIN_FLOAT, min=MIN_FLOAT, max=MAX_FLOAT, step=0.01, tooltip=TOOLTIP_MIN))
        schema.inputs.append(io.Float.Input("max", default=MAX_FLOAT, min=MIN_FLOAT, max=MAX_FLOAT, step=0.01, tooltip=TOOLTIP_MAX))
        # Step size is weird in Blender, value of 1 gives a step of 0.1, so I'm deactivating it for now
        # schema.inputs.append(io.Float.Input("step", default=0.01, min=0.01, max=MAX_FLOAT, step=0.01, tooltip=TOOLTIP_STEP))

        # Overwrite value input to overwrite min/max/step
        for i, input in enumerate(schema.inputs):
            if input.id == "value":
                schema.inputs[i] = io.Float.Input("value", default=0.0, min=MIN_FLOAT, max=MAX_FLOAT, step=0.01)
                break
        return schema

    @classmethod
    def execute(cls, value: float, order: int, default: float, min: float, max: float, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(value)
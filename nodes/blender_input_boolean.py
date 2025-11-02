from comfy_api.latest import io
from comfy_extras.nodes_primitive import Boolean
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_ORDER
)


class BlenderInputBoolean(Boolean):
    """Display a boolean input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputBoolean"
        schema.display_name="Blender Input Boolean"
        schema.description="Display a boolean input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.Boolean.Input("default", default=False, tooltip=TOOLTIP_DEFAULT))
        return schema

    @classmethod
    def execute(cls, value: bool, order: int, default: bool, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(value)
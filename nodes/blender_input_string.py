import os

from comfy_api.latest import io
from comfy_extras.nodes_primitive import String
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_FORMAT_PATH,
    TOOLTIP_ORDER
)


class BlenderInputString(String):
    """Display a string input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputString"
        schema.display_name="Blender Input String"
        schema.description="Display a string input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.String.Input("default", default="", tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Boolean.Input("format_path", default=False, tooltip=TOOLTIP_FORMAT_PATH))
        return schema

    @classmethod
    def execute(cls, value: str, order: int, default: str, format_path: bool, **kwargs) -> io.NodeOutput:
        value = str(os.path.normpath(value)) if format_path else value
        return io.NodeOutput(value)
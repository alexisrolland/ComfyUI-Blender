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


class BlenderInputCombo(String):
    """Display a combo box input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputCombo"
        schema.display_name="Blender Input Combo Box"
        schema.description="Display a combo box input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.String.Input("default", default="", tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Boolean.Input("format_path", default=False, tooltip=TOOLTIP_FORMAT_PATH))
        schema.inputs.append(io.String.Input("list", default="", multiline=True, tooltip="list of values displayed in the combo box in the Blender add-on (one item per line)."))
        schema.outputs = [io.AnyType.Output(display_name="COMBO")]  # Do not change the display_name, it is used in the JS code to find the output socket
        return schema

    @classmethod
    def execute(cls, value: str, order: int, default: str, format_path: bool, list: str, **kwargs) -> io.NodeOutput:
        value = str(os.path.normpath(value)) if format_path else value
        return io.NodeOutput(value)
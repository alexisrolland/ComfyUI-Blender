from comfy_api.latest import io
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_ORDER
)


class BlenderInputGroup(io.ComfyNode):
    """Group inputs into a box in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="BlenderInputGroup",
            display_name="Blender Input Group",
            description="Group inputs into a box in the Blender add-on.",
            category="blender",
            inputs=[
                io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER),
                io.Boolean.Input("show_title", default=False, tooltip="Display the node title as a label in the Blender add-on."),
                io.Boolean.Input("compact", default=False, tooltip="Display inputs with a compact layout in the Blender add-on.")
            ],
            outputs=[io.Custom("GROUP").Output("group", display_name="group")]
        )

    @classmethod
    def execute(cls, order: int, show_title: bool, compact: bool) -> io.NodeOutput:
        return io.NodeOutput(True)
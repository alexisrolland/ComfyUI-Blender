from comfy_api.latest import io
from comfy_extras.nodes_custom_sampler import KSamplerSelect
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_ORDER
)

class BlenderInputSampler(KSamplerSelect):
    """Display the list of samplers in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputSampler"
        schema.display_name="Blender Input Sampler"
        schema.description="Display the list of samplers in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.String.Input("default", tooltip=TOOLTIP_DEFAULT))
        schema.outputs = [io.AnyType.Output(display_name="SAMPLER"))]
        return schema

    @classmethod
    def execute(self, sampler_name, order: int, default: str, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(sampler_name)
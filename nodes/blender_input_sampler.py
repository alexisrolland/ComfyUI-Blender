from comfy_extras.nodes_custom_sampler import KSamplerSelect
from comfy.comfy_types.node_typing import IO
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_ORDER
)

class BlenderInputSampler(KSamplerSelect):
    """Display the list of samplers in the Blender add-on."""
    CATEGORY = "blender"
    FUNCTION = "execute"
    RETURN_TYPES = (IO.ANY,)

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False, "tooltip": TOOLTIP_ORDER})
        INPUT_TYPES["required"]["default"] = (IO.STRING, {"default": "", "tooltip": TOOLTIP_DEFAULT})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES

    def execute(self, sampler_name, order: int, default: str, **kwargs):
        return super().get_sampler(sampler_name)
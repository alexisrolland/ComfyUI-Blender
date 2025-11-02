import os

from comfy.comfy_types.node_typing import IO
from nodes import LoraLoaderModelOnly
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_ORDER
)


class BlenderInputLoadLora(LoraLoaderModelOnly):
    """Node used by ComfyUI Blender add-on to select a LoRA model name from the loras folder of the ComfyUI server."""
    CATEGORY = "blender"
    FUNCTION = "execute"

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

    def execute(self, model, lora_name, strength_model, order: int, default: str, **kwargs):
        lora_name = str(os.path.normpath(lora_name))
        return super().load_lora_model_only(model, lora_name, strength_model)
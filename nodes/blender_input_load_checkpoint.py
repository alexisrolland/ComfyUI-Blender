import os

from comfy.comfy_types.node_typing import IO
from nodes import CheckpointLoaderSimple
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_DEFAULT,
    TOOLTIP_ORDER
)


class BlenderInputLoadCheckpoint(CheckpointLoaderSimple):
    """Node used by ComfyUI Blender add-on to select a model name from the checkpoints folder of the ComfyUI server."""
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

    def execute(self, ckpt_name, order: int, default: str, **kwargs):
        ckpt_name = str(os.path.normpath(ckpt_name))
        return super().load_checkpoint(ckpt_name)
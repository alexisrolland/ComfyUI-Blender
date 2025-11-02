from comfy.comfy_types.node_typing import IO
from nodes import LoadImageMask
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_ORDER
)


class BlenderInputLoadMask(LoadImageMask):
    """Node used by ComfyUI Blender add-on to input a mask in a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False, "tooltip": TOOLTIP_ORDER})
        del INPUT_TYPES["required"]["channel"]  # Remove the channel widget as we hard code it to alpha below

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES
    
    def execute(self, image, order, **kwargs):
        result = super().load_image(image, "alpha")  # Enforce use of alpha channel for mask
        result = result[1:]  # Remove the image output from the tuple
        return result

    @classmethod
    def IS_CHANGED(s, image, order, **kwargs):
        return super().IS_CHANGED(image)
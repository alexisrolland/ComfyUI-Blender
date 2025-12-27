from comfy.comfy_types.node_typing import IO
from nodes import LoadImage
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_ORDER
)


class BlenderInputLoadImage(LoadImage):
    """Node used by ComfyUI Blender add-on to input an image in a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False, "tooltip": TOOLTIP_ORDER})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES
    
    def execute(self, image, order, **kwargs):
        result = super().load_image(image)
        return result

    @classmethod
    def IS_CHANGED(s, image, order, **kwargs):
        return super().IS_CHANGED(image)
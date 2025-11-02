from comfy.comfy_types.node_typing import IO
from nodes import SaveImage


class BlenderOutputSaveImage(SaveImage):
    """Node used by ComfyUI Blender add-on to capture an image output from a workflow."""
    CATEGORY = "blender"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["filename_prefix"] = (IO.STRING, {"default": "blender"})
        return INPUT_TYPES
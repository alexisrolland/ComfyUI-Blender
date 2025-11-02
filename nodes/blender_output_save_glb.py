from comfy.comfy_types.node_typing import IO
from comfy_extras.nodes_hunyuan3d import SaveGLB


class BlenderOutputSaveGlb(SaveGLB):
    """Node used by ComfyUI Blender add-on to GLB file output from a workflow."""
    CATEGORY = "blender"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["filename_prefix"] = (IO.STRING, {"default": "3d/blender"})
        return INPUT_TYPES
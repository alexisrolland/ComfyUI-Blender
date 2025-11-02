import os

import folder_paths
from comfy.comfy_types.node_typing import IO
from .utils import (
    MAX_INT,
    MIN_INT,
    TOOLTIP_ORDER
)


class BlenderInputLoad3D():
    """Node used by ComfyUI Blender add-on to input a 3D asset in a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"
    RETURN_TYPES = (IO.ANY,)

    @staticmethod
    def normalize_path(path):
        """Ensure the model path is in the same format as ComfyUI native Load 3D node."""
        return path.replace("\\", "/")

    @classmethod
    def INPUT_TYPES(s):
        # Get list of 3D files
        input_dir = os.path.join(folder_paths.get_input_directory(), "3d")
        os.makedirs(input_dir, exist_ok=True)
        files = [s.normalize_path(os.path.join("3d", f)) for f in os.listdir(input_dir) if f.endswith((".gltf", ".glb", ".obj", ".fbx", ".stl"))]

        INPUT_TYPES = {"required": {}}
        INPUT_TYPES["required"]["model_file"] = (sorted(files), {"file_upload": True})
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False, "tooltip": TOOLTIP_ORDER})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES

    def execute(self, model_file, order, **kwargs):
        return (model_file,)
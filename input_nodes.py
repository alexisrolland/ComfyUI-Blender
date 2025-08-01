import os

import folder_paths
from comfy_extras.nodes_primitive import Boolean, Float, Int, String, StringMultiline
from comfy.comfy_types.node_typing import IO
from nodes import LoadImage

# Enforce min/max int and float according to Blender limitation
MIN_FLOAT = -2147483648.00
MIN_INT = -2147483648
MAX_FLOAT = 2147483647.00
MAX_INT = 2147483647


class BlenderInputBoolean(Boolean):
    """Node used by ComfyUI Blender add-on to input a boolean in a workflow."""
    CATEGORY = "blender/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.BOOLEAN, {})
        return INPUT_TYPES

    def execute(self, value: bool, order: int, default: bool) -> tuple[bool]:
        return (value,)

class BlenderInputCombo(String):
    """Node used by ComfyUI Blender add-on to input a value from a combo box in a workflow."""
    CATEGORY = "blender/inputs"
    RETURN_TYPES = (IO.ANY,)

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.STRING, {"default": ""})
        INPUT_TYPES["required"]["format_path"] = (IO.BOOLEAN, {"default": False, "tooltip": "If the string value is a file path, format it to be compatible with the operating system where ComfyUI is running."})
        INPUT_TYPES["required"]["list"] = (IO.STRING, {"default": "", "multiline": True})
        return INPUT_TYPES

    def execute(self, value: str, order: int, default: str, format_path: bool, list: str) -> tuple[str]:
        value = str(os.path.normpath(value)) if format_path else value
        return (value,)

class BlenderInputFloat(Float):
    """Node used by ComfyUI Blender add-on to input a float in a workflow."""
    CATEGORY = "blender/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["value"] = (IO.FLOAT, {"default": 0.00, "min": MIN_FLOAT, "max": MAX_FLOAT, "step": 0.01})
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.FLOAT, {"default": 0.00, "min": MIN_FLOAT, "max": MAX_FLOAT, "step": 0.01})
        INPUT_TYPES["required"]["min"] = (IO.FLOAT, {"default": MIN_FLOAT, "min": MIN_FLOAT, "max": MAX_FLOAT, "step": 0.01})
        INPUT_TYPES["required"]["max"] = (IO.FLOAT, {"default": MAX_FLOAT, "min": MIN_FLOAT, "max": MAX_FLOAT, "step": 0.01})
        # Step size is weird in Blender, value of 1 gives a step of 0.1, so I'm deactivating it for now
        # INPUT_TYPES["required"]["step"] = (IO.FLOAT, {"default": 0.01, "min": 0.01, "max": MAX_FLOAT, "step": 0.01})
        return INPUT_TYPES

    def execute(self, value: float, order: int, default: float, min: float, max: float) -> tuple[int]:
        return (value,)

class BlenderInputInt(Int):
    """Node used by ComfyUI Blender add-on to input an integer in a workflow."""
    CATEGORY = "blender/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["value"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "step": 1})
        INPUT_TYPES["required"]["min"] = (IO.INT, {"default": MIN_INT, "min": MIN_INT, "max": MAX_INT, "step": 1})
        INPUT_TYPES["required"]["max"] = (IO.INT, {"default": MAX_INT, "min": MIN_INT, "max": MAX_INT, "step": 1})
        INPUT_TYPES["required"]["step"] = (IO.INT, {"default": 1, "min": 1, "max": MAX_INT, "step": 1})
        INPUT_TYPES["required"]["camera_width"] = (IO.BOOLEAN, {"default": False, "tooltip": "Display a button to set/get the camera width."})
        INPUT_TYPES["required"]["camera_height"] = (IO.BOOLEAN, {"default": False, "tooltip": "Display a button to set/get the camera height."})
        return INPUT_TYPES

    def execute(self, value: int, order: int, default: int, min: int, max: int, step: int, camera_width: bool, camera_height: bool) -> tuple[int]:
        return (value,)

class BlenderInputLoad3D():
    """Node used by ComfyUI Blender add-on to input a 3D asset in a workflow."""
    CATEGORY = "blender/inputs"
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
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        return INPUT_TYPES

    def execute(self, model_file, order):
        return (model_file,)

class BlenderInputLoadImage(LoadImage):
    """Node used by ComfyUI Blender add-on to input an image in a workflow."""
    CATEGORY = "blender/inputs"
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        return INPUT_TYPES
    
    def execute(self, image, order):
        return super().load_image(image)

    @classmethod
    def IS_CHANGED(s, image, order):
        return super().IS_CHANGED(image)

class BlenderInputSeed(BlenderInputInt):
    """
    Node used by ComfyUI Blender add-on to input a seed value in a workflow.
    This node reuses the most parameters from the BlenderInputInt node, but the display is different in Blender.
    """
    CATEGORY = "blender/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["min"] = (IO.INT, {"default": 0, "min": 0, "max": MAX_INT, "step": 1})
        return INPUT_TYPES

class BlenderInputString(String):
    """Node used by ComfyUI Blender add-on to input a string in a workflow."""
    CATEGORY = "blender/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.STRING, {"default": ""})
        INPUT_TYPES["required"]["format_path"] = (IO.BOOLEAN, {"default": False, "tooltip": "If the string value is a file path, format it to be compatible with the operating system where ComfyUI is running."})
        return INPUT_TYPES

    def execute(self, value: str, order: int, default: str, format_path: bool) -> tuple[str]:
        value = str(os.path.normpath(value)) if format_path else value
        return (value,)

class BlenderInputStringMultiline(StringMultiline):
    """Node used by ComfyUI Blender add-on to input a multiline string in a workflow."""
    CATEGORY = "blender/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.STRING, {"default": "", "multiline": True})
        INPUT_TYPES["required"]["format_path"] = (IO.BOOLEAN, {"default": False, "tooltip": "If the string value is a file path, format it to be compatible with the operating system where ComfyUI is running."})
        return INPUT_TYPES

    def execute(self, value: str, order: int, default: str, format_path: bool) -> tuple[str]:
        value = str(os.path.normpath(value)) if format_path else value
        return (value,)
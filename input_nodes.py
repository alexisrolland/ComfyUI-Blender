from comfy_extras.nodes_primitive import Float, Int, String, StringMultiline

class BlenderInputFloat(Float):
    """Node used by ComfyUI Blender Plugin to input a float in a workflow."""
    CATEGORY = "blender plugin/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        if "optional" not in INPUT_TYPES:
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["default"] = ("FLOAT", {})
        INPUT_TYPES["optional"]["min"] = ("FLOAT", {})
        INPUT_TYPES["optional"]["max"] = ("FLOAT", {})
        return INPUT_TYPES
    
    def execute(self, value: float, default: float=0, min: float=0, max: float=0) -> tuple[int]:
        return (value,)

class BlenderInputInt(Int):
    """Node used by ComfyUI Blender Plugin to input an integer in a workflow."""
    CATEGORY = "blender plugin/inputs"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        if "optional" not in INPUT_TYPES:
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["default"] = ("INT", {})
        INPUT_TYPES["optional"]["min"] = ("INT", {})
        INPUT_TYPES["optional"]["max"] = ("INT", {})
        return INPUT_TYPES
    
    def execute(self, value: int, default: int=0, min: int=0, max: int=0) -> tuple[int]:
        return (value,)

class BlenderInputString(String):
    """Node used by ComfyUI Blender Plugin to input a string in a workflow."""
    CATEGORY = "blender plugin/inputs"

class BlenderInputStringMultiline(StringMultiline):
    """Node used by ComfyUI Blender Plugin to input a multiline string in a workflow."""
    CATEGORY = "blender plugin/inputs"
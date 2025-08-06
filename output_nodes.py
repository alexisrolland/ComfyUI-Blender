from comfy.comfy_types.node_typing import IO
from comfy_extras.nodes_hunyuan3d import SaveGLB
from nodes import SaveImage


class BlenderOutputDownload3D():
    """Node used by ComfyUI Blender add-on to capture a 3D output from a workflow."""
    CATEGORY = "blender/outputs"
    FUNCTION = "execute"
    OUTPUT_NODE = True
    RETURN_TYPES = ()

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = {"required": {}}
        INPUT_TYPES["required"]["model_file"] = (IO.STRING, {"forceInput": True})
        return INPUT_TYPES

    def execute(self, model_file: str) -> dict:
        websocket_message = {}
        websocket_message["ui"] = {}
        websocket_message["ui"]["3d"] = [model_file]
        return websocket_message

class BlenderOutputSaveGlb(SaveGLB):
    """Node used by ComfyUI Blender add-on to GLB file output from a workflow."""
    CATEGORY = "blender/outputs"

class BlenderOutputSaveImage(SaveImage):
    """Node used by ComfyUI Blender add-on to capture an image output from a workflow."""
    CATEGORY = "blender/outputs"
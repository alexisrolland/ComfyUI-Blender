import os

from comfy.comfy_types.node_typing import IO


class BlenderOutputDownload3D():
    """Node used by ComfyUI Blender add-on to capture a 3D output from a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"
    OUTPUT_NODE = True
    RETURN_TYPES = ()

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = {"required": {}}
        INPUT_TYPES["required"]["model_file"] = (IO.STRING, {"forceInput": True})
        return INPUT_TYPES

    def execute(self, model_file: str) -> dict:

        # Get results
        subfolder, filename = os.path.split(model_file)
        result = {"filename": filename, "subfolder": subfolder, "type": "output"}

        # Push results
        websocket_message = {}
        websocket_message["ui"] = {}
        websocket_message["ui"]["3d"] = [result]
        return websocket_message
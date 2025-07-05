from nodes import SaveImage

class BlenderOutputSaveImage(SaveImage):
    """Node used by ComfyUI Blender Plugin to capture the output from a workflow."""
    CATEGORY = "blender plugin/outputs"
from nodes import SaveImage

class BlenderOutputSaveImage(SaveImage):
    """Node used by ComfyUI Blender add-on to capture the output from a workflow."""
    CATEGORY = "blender/outputs"
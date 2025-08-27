from .input_nodes import (
    BlenderInputBoolean,
    BlenderInputCheckpointLoader,
    BlenderInputCombo,
    BlenderInputFloat,
    BlenderInputGroup,
    BlenderInputInt,
    BlenderInputLoad3D,
    BlenderInputLoadImage,
    BlenderInputSeed,
    BlenderInputString,
    BlenderInputStringMultiline,
    BlenderInputUnetLoader
)
from .output_nodes import (
    BlenderOutputDownload3D,
    BlenderOutputSaveGlb,
    BlenderOutputSaveImage
)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "BlenderInputBoolean": BlenderInputBoolean,
    "BlenderInputCheckpointLoader": BlenderInputCheckpointLoader,
    "BlenderInputCombo": BlenderInputCombo,
    "BlenderInputFloat": BlenderInputFloat,
    "BlenderInputGroup": BlenderInputGroup,
    "BlenderInputInt": BlenderInputInt,
    "BlenderInputLoad3D": BlenderInputLoad3D,
    "BlenderInputLoadImage": BlenderInputLoadImage,
    "BlenderInputSeed": BlenderInputSeed,
    "BlenderInputString": BlenderInputString,
    "BlenderInputStringMultiline": BlenderInputStringMultiline,
    "BlenderInputUnetLoader": BlenderInputUnetLoader,
    "BlenderOutputDownload3D": BlenderOutputDownload3D,
    "BlenderOutputSaveGlb": BlenderOutputSaveGlb,
    "BlenderOutputSaveImage": BlenderOutputSaveImage
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderInputBoolean": "Blender Input Boolean",
    "BlenderInputCheckpointLoader": "Blender Input Load Checkpoint",
    "BlenderInputCombo": "Blender Input Combo",
    "BlenderInputFloat": "Blender Input Float",
    "BlenderInputGroup": "Blender Input Group",
    "BlenderInputInt": "Blender Input Integer",
    "BlenderInputLoad3D": "Blender Input Load 3D",
    "BlenderInputLoadImage": "Blender Input Load Image",
    "BlenderInputSeed": "Blender Input Seed",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline",
    "BlenderInputUnetLoader": "Blender Input Load Diffusion Model",
    "BlenderOutputDownload3D": "Blender Output Download 3D",
    "BlenderOutputSaveGlb": "Blender Output Save GLB",
    "BlenderOutputSaveImage": "Blender Output Save Image"
}

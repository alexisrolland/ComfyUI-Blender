from .input_nodes import (
    BlenderInputBoolean,
    BlenderInputCombo,
    BlenderInputFloat,
    BlenderInputGroup,
    BlenderInputInt,
    BlenderInputLoad3D,
    BlenderInputLoadCheckpoint,
    BlenderInputLoadDiffusionModel,
    BlenderInputLoadImage,
    BlenderInputLoadLora,
    BlenderInputLoadMask,
    BlenderInputSeed,
    BlenderInputString,
    BlenderInputStringMultiline
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
    "BlenderInputCombo": BlenderInputCombo,
    "BlenderInputFloat": BlenderInputFloat,
    "BlenderInputGroup": BlenderInputGroup,
    "BlenderInputInt": BlenderInputInt,
    "BlenderInputLoad3D": BlenderInputLoad3D,
    "BlenderInputLoadCheckpoint": BlenderInputLoadCheckpoint,
    "BlenderInputLoadDiffusionModel": BlenderInputLoadDiffusionModel,
    "BlenderInputLoadImage": BlenderInputLoadImage,
    "BlenderInputLoadLora": BlenderInputLoadLora,
    "BlenderInputLoadMask": BlenderInputLoadMask,
    "BlenderInputSeed": BlenderInputSeed,
    "BlenderInputString": BlenderInputString,
    "BlenderInputStringMultiline": BlenderInputStringMultiline,
    "BlenderOutputDownload3D": BlenderOutputDownload3D,
    "BlenderOutputSaveGlb": BlenderOutputSaveGlb,
    "BlenderOutputSaveImage": BlenderOutputSaveImage
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderInputBoolean": "Blender Input Boolean",
    "BlenderInputCombo": "Blender Input Combo",
    "BlenderInputFloat": "Blender Input Float",
    "BlenderInputGroup": "Blender Input Group",
    "BlenderInputInt": "Blender Input Integer",
    "BlenderInputLoad3D": "Blender Input Load 3D",
    "BlenderInputLoadCheckpoint": "Blender Input Load Checkpoint",
    "BlenderInputLoadDiffusionModel": "Blender Input Load Diffusion Model",
    "BlenderInputLoadImage": "Blender Input Load Image",
    "BlenderInputLoadLora": "Blender Input Load LoRA",
    "BlenderInputLoadMask": "Blender Input Load Mask",
    "BlenderInputSeed": "Blender Input Seed",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline",
    "BlenderOutputDownload3D": "Blender Output Download 3D",
    "BlenderOutputSaveGlb": "Blender Output Save GLB",
    "BlenderOutputSaveImage": "Blender Output Save Image"
}

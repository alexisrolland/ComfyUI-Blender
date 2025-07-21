from .input_nodes import (
    BlenderInputBoolean,
    BlenderInputCombo,
    BlenderInputFloat,
    BlenderInputInt,
    BlenderInputLoad3D,
    BlenderInputLoadImage,
    BlenderInputSeed,
    BlenderInputString,
    BlenderInputStringMultiline
)
from .output_nodes import (
    BlenderOutputDownload3D,
    BlenderOutputSaveImage
)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "BlenderInputBoolean": BlenderInputBoolean,
    "BlenderInputCombo": BlenderInputCombo,
    "BlenderInputFloat": BlenderInputFloat,
    "BlenderInputInt": BlenderInputInt,
    "BlenderInputLoad3D": BlenderInputLoad3D,
    "BlenderInputLoadImage": BlenderInputLoadImage,
    "BlenderInputSeed": BlenderInputSeed,
    "BlenderInputString": BlenderInputString,
    "BlenderInputStringMultiline": BlenderInputStringMultiline,
    "BlenderOutputDownload3D": BlenderOutputDownload3D,
    "BlenderOutputSaveImage": BlenderOutputSaveImage
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderInputBoolean": "Blender Input Boolean",
    "BlenderInputCombo": "Blender Input Combo",
    "BlenderInputFloat": "Blender Input Float",
    "BlenderInputInt": "Blender Input Integer",
    "BlenderInputLoad3D": "Blender Input Load 3D",
    "BlenderInputLoadImage": "Blender Input Load Image",
    "BlenderInputSeed": "Blender Input Seed",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline",
    "BlenderOutputDownload3D": "Blender Output Download 3D",
    "BlenderOutputSaveImage": "Blender Output Save Image"
}

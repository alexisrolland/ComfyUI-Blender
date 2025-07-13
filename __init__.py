from .input_nodes import (
    BlenderInputBoolean,
    BlenderInputCombo,
    BlenderInputFloat,
    BlenderInputInt,
    BlenderInputLoadImage,
    BlenderInputString,
    BlenderInputStringMultiline
)
from .output_nodes import (
    BlenderOutputSaveImage
)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "BlenderInputBoolean": BlenderInputBoolean,
    "BlenderInputCombo": BlenderInputCombo,
    "BlenderInputFloat": BlenderInputFloat,
    "BlenderInputInt": BlenderInputInt,
    "BlenderInputLoadImage": BlenderInputLoadImage,
    "BlenderInputString": BlenderInputString,
    "BlenderInputStringMultiline": BlenderInputStringMultiline,
    "BlenderOutputSaveImage": BlenderOutputSaveImage
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderInputBoolean": "Blender Input Boolean",
    "BlenderInputCombo": "Blender Input Combo",
    "BlenderInputFloat": "Blender Input Float",
    "BlenderInputInt": "Blender Input Integer",
    "BlenderInputLoadImage": "Blender Input Load Image",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline",
    "BlenderOutputSaveImage": "Blender Output Save Image"
}

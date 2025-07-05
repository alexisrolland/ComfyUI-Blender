from .input_nodes import (
    BlenderInputCombo,
    BlenderInputFloat,
    BlenderInputInt,
    BlenderInputString,
    BlenderInputStringMultiline
)
from .output_nodes import (
    BlenderOutputSaveImage
)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "BlenderInputCombo": BlenderInputCombo,
    "BlenderInputFloat": BlenderInputFloat,
    "BlenderInputInt": BlenderInputInt,
    "BlenderInputString": BlenderInputString,
    "BlenderInputStringMultiline": BlenderInputStringMultiline,
    "BlenderOutputSaveImage": BlenderOutputSaveImage
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderInputCombo": "Blender Input Combo",
    "BlenderInputFloat": "Blender Input Float",
    "BlenderInputInt": "Blender Input Integer",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline",
    "BlenderOutputSaveImage": "Blender Output Save Image"
}

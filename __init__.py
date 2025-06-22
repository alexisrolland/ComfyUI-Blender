from .input_nodes import (
    BlenderInputFloat,
    BlenderInputInt,
    BlenderInputString,
    BlenderInputStringMultiline
)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "BlenderInputFloat": BlenderInputFloat,
    "BlenderInputInt": BlenderInputInt,
    "BlenderInputString": BlenderInputString,
    "BlenderInputStringMultiline": BlenderInputStringMultiline
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "BlenderInputFloat": "Blender Input Float",
    "BlenderInputInt": "Blender Input Integer",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline"
}

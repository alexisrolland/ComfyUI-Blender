from comfy_extras.nodes_preview_any import PreviewAny


class BlenderOutputString(PreviewAny):
    """Node used by ComfyUI Blender add-on to capture an text output from a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["string"] = INPUT_TYPES["required"]["source"]  # Rename input socket source to string
        del INPUT_TYPES["required"]["source"]
        return INPUT_TYPES
    
    def execute(self, string: str):
        return self.main(source=string)
from comfy.comfy_types.node_typing import IO
from comfy_api.latest import io
from comfy_extras.nodes_hunyuan3d import SaveGLB


class BlenderOutputSaveGlb(SaveGLB):
    """
    Node used by ComfyUI Blender add-on to GLB file output from a workflow.
    """

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderOutputSaveGlb"
        schema.display_name="Blender Output Save Glb"
        schema.description="Node to allow blender application to capture a GLB Object Output from a workflow."
        schema.category = "blender"

        # Overwrite value input to overwrite min/max/step
        for i, input in enumerate(schema.inputs):
            if input.id == "filename_prefix":
                schema.inputs[i] = IO.String.Input("filename_prefix", default="mesh/Blender"),
                break

        return schema

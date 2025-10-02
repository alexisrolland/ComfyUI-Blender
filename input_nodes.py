import os

import folder_paths
from comfy_api.latest import io
from comfy_extras.nodes_primitive import Boolean, Float, Int, String, StringMultiline
from comfy.comfy_types.node_typing import IO
from nodes import CheckpointLoaderSimple, LoadImage, LoraLoaderModelOnly, UNETLoader


# Enforce min/max int and float according to Blender limitation
MIN_FLOAT = -2147483648.00
MIN_INT = -2147483648
MAX_FLOAT = 2147483647.00
MAX_INT = 2147483647

# Static variables for standard inputs
TOOLTIP_ORDER = "Position of the input in the Blender add-on."
TOOLTIP_DEFAULT = "Default value of the input in the Blender add-on."
TOOLTIP_FORMAT_PATH = "If the string value is a file path, format it to be compatible with the operating system where ComfyUI is running."
TOOLTIP_MIN = "Minimum value of the input in the Blender add-on."
TOOLTIP_MAX = "Maximum value of the input in the Blender add-on."
TOOLTIP_STEP = "Step size of the input in the Blender add-on."


class BlenderInputBoolean(Boolean):
    """Display a boolean input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputBoolean"
        schema.display_name="Blender Input Boolean"
        schema.description="Display a boolean input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", tooltip=TOOLTIP_ORDER, default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False))
        schema.inputs.append(io.Boolean.Input("default", tooltip=TOOLTIP_DEFAULT, default=False))
        return schema

    @classmethod
    def execute(cls, value: bool, order: int, default: bool, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(value)


class BlenderInputCombo(String):
    """Display a combo box input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputCombo"
        schema.display_name="Blender Input Combo Box"
        schema.description="Display a combo box input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.String.Input("default", default="", tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Boolean.Input("format_path", default=False, tooltip=TOOLTIP_FORMAT_PATH))
        schema.inputs.append(io.String.Input("list", default="", multiline=True, tooltip="list of values displayed in the combo box in the Blender add-on (one item per line)."))
        schema.outputs = [io.AnyType.Output()]
        return schema

    @classmethod
    def execute(cls, value: str, order: int, default: str, format_path: bool, list: str, **kwargs) -> io.NodeOutput:
        value = str(os.path.normpath(value)) if format_path else value
        return io.NodeOutput(value)


class BlenderInputFloat(Float):
    """Display a float input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputFloat"
        schema.display_name="Blender Input Float"
        schema.description="Display a float input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.Float.Input("default", default=0.0, tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Float.Input("min", default=MIN_FLOAT, min=MIN_FLOAT, max=MAX_FLOAT, step=0.01, tooltip=TOOLTIP_MIN))
        schema.inputs.append(io.Float.Input("max", default=MAX_FLOAT, min=MIN_FLOAT, max=MAX_FLOAT, step=0.01, tooltip=TOOLTIP_MAX))
        # Step size is weird in Blender, value of 1 gives a step of 0.1, so I'm deactivating it for now
        # schema.inputs.append(io.Float.Input("step", default=0.01, min=0.01, max=MAX_FLOAT, step=0.01, tooltip=TOOLTIP_STEP))

        # Overwrite value input to overwrite min/max/step
        for i, input in enumerate(schema.inputs):
            if input.id == "value":
                schema.inputs[i] = io.Float.Input("value", default=0.0, min=MIN_FLOAT, max=MAX_FLOAT, step=0.01)
                break
        return schema

    @classmethod
    def execute(cls, value: float, order: int, default: float, min: float, max: float, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(value)


class BlenderInputGroup(io.ComfyNode):
    """Group inputs into a box in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="BlenderInputGroup",
            display_name="Blender Input Group",
            description="Group inputs into a box in the Blender add-on.",
            category="blender",
            inputs=[
                io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER),
                io.Boolean.Input("show_title", default=False, tooltip="Display the node title as a label in the Blender add-on."),
                io.Boolean.Input("compact", default=False, tooltip="Display inputs with a compact layout in the Blender add-on.")
            ],
            outputs=[io.Custom("GROUP").Output("group", display_name="group")]
        )

    @classmethod
    def execute(cls, order: int, show_title: bool, compact: bool) -> io.NodeOutput:
        return io.NodeOutput(True)


class BlenderInputInt(Int):
    """Display an integer input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputInt"
        schema.display_name="Blender Input Integer"
        schema.description="Display an integer input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.Int.Input("default", default=0, tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Int.Input("min", default=MIN_INT, min=MIN_INT, max=MAX_INT, step=1, tooltip=TOOLTIP_MIN))
        schema.inputs.append(io.Int.Input("max", default=MAX_INT, min=MIN_INT, max=MAX_INT, step=1, tooltip=TOOLTIP_MAX))
        schema.inputs.append(io.Int.Input("step", default=1, min=1, max=MAX_INT, step=1, tooltip=TOOLTIP_STEP))
        schema.inputs.append(io.Boolean.Input("camera_width", default=False, tooltip="Display a button to set/get the camera width."))
        schema.inputs.append(io.Boolean.Input("camera_height", default=False, tooltip="Display a button to set/get the camera height."))

        # Overwrite value input to remove control_after_generate and overwrite min/max/step
        for i, input in enumerate(schema.inputs):
            if input.id == "value":
                schema.inputs[i] = io.Int.Input("value", default=0, min=MIN_INT, max=MAX_INT, step=1, control_after_generate=False)
                break
        return schema

    @classmethod
    def execute(cls, value: int, order: int, default: int, min: int, max: int, step: int, camera_width: bool, camera_height: bool, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(value)


class BlenderInputLoad3D():
    """Node used by ComfyUI Blender add-on to input a 3D asset in a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"
    RETURN_TYPES = (IO.ANY,)

    @staticmethod
    def normalize_path(path):
        """Ensure the model path is in the same format as ComfyUI native Load 3D node."""
        return path.replace("\\", "/")

    @classmethod
    def INPUT_TYPES(s):
        # Get list of 3D files
        input_dir = os.path.join(folder_paths.get_input_directory(), "3d")
        os.makedirs(input_dir, exist_ok=True)
        files = [s.normalize_path(os.path.join("3d", f)) for f in os.listdir(input_dir) if f.endswith((".gltf", ".glb", ".obj", ".fbx", ".stl"))]

        INPUT_TYPES = {"required": {}}
        INPUT_TYPES["required"]["model_file"] = (sorted(files), {"file_upload": True})
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES

    def execute(self, model_file, order, **kwargs):
        return (model_file,)


class BlenderInputLoadCheckpoint(CheckpointLoaderSimple):
    """Node used by ComfyUI Blender add-on to select a model name from the checkpoints folder of the ComfyUI server."""
    CATEGORY = "blender"
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.STRING, {"default": ""})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES

    def execute(self, ckpt_name, order: int, default: str, **kwargs):
        ckpt_name = str(os.path.normpath(ckpt_name))
        return super().load_checkpoint(ckpt_name)


class BlenderInputLoadDiffusionModel(UNETLoader):
    """Node used by ComfyUI Blender add-on to select a model name from the diffusion models folder of the ComfyUI server."""
    CATEGORY = "blender"
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.STRING, {"default": ""})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES

    def execute(self, unet_name, weight_dtype, order: int, default: str, **kwargs):
        unet_name = str(os.path.normpath(unet_name))
        return super().load_unet(unet_name, weight_dtype)


class BlenderInputLoadImage(LoadImage):
    """Node used by ComfyUI Blender add-on to input an image in a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES
    
    def execute(self, image, order, **kwargs):
        result = super().load_image(image)
        result = result[:-1]  # Remove the mask output from the tuple
        return result

    @classmethod
    def IS_CHANGED(s, image, order, **kwargs):
        return super().IS_CHANGED(image)


class BlenderInputLoadLora(LoraLoaderModelOnly):
    """Node used by ComfyUI Blender add-on to select a LoRA model name from the loras folder of the ComfyUI server."""
    CATEGORY = "blender"
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})
        INPUT_TYPES["required"]["default"] = (IO.STRING, {"default": ""})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES

    def execute(self, model, lora_name, strength_model, order: int, default: str, **kwargs):
        lora_name = str(os.path.normpath(lora_name))
        return super().load_lora_model_only(model, lora_name, strength_model)


class BlenderInputLoadMask(LoadImage):
    """Node used by ComfyUI Blender add-on to input a mask in a workflow."""
    CATEGORY = "blender"
    FUNCTION = "execute"
    RETURN_TYPES = ("MASK",)

    @classmethod
    def INPUT_TYPES(s):
        INPUT_TYPES = super().INPUT_TYPES()
        INPUT_TYPES["required"]["order"] = (IO.INT, {"default": 0, "min": MIN_INT, "max": MAX_INT, "control_after_generate": False})

        # Create optional input key
        if not INPUT_TYPES.get("optional", None):
            INPUT_TYPES["optional"] = {}
        INPUT_TYPES["optional"]["group"] = ("GROUP", {"forceInput":True})
        return INPUT_TYPES
    
    def execute(self, image, order, **kwargs):
        result = super().load_image(image)
        result = result[1:]  # Remove the image output from the tuple
        return result

    @classmethod
    def IS_CHANGED(s, image, order, **kwargs):
        return super().IS_CHANGED(image)


class BlenderInputSeed(Int):
    """Display a seed input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputSeed"
        schema.display_name="Blender Input Seed"
        schema.description="Display seed input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.Int.Input("default", default=0, tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Int.Input("min", default=MIN_INT, min=MIN_INT, max=MAX_INT, step=1, tooltip=TOOLTIP_MIN))
        schema.inputs.append(io.Int.Input("max", default=MAX_INT, min=MIN_INT, max=MAX_INT, step=1, tooltip=TOOLTIP_MAX))
        schema.inputs.append(io.Int.Input("step", default=1, min=1, max=MAX_INT, step=1, tooltip=TOOLTIP_STEP))

        # Overwrite value input to remove control_after_generate and overwrite min/max/step
        for i, input in enumerate(schema.inputs):
            if input.id == "value":
                schema.inputs[i] = io.Int.Input("value", default=0, min=MIN_INT, max=MAX_INT, step=1, control_after_generate=False)
                break
        return schema

    @classmethod
    def execute(cls, value: int, order: int, default: int, min: int, max: int, step: int, **kwargs) -> io.NodeOutput:
        return io.NodeOutput(value)


class BlenderInputString(String):
    """Display a string input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputString"
        schema.display_name="Blender Input String"
        schema.description="Display a string input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.String.Input("default", default="", tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Boolean.Input("format_path", default=False, tooltip=TOOLTIP_FORMAT_PATH))
        return schema

    @classmethod
    def execute(cls, value: str, order: int, default: str, format_path: bool, **kwargs) -> io.NodeOutput:
        value = str(os.path.normpath(value)) if format_path else value
        return io.NodeOutput(value)


class BlenderInputStringMultiline(StringMultiline):
    """Display a string input in the Blender add-on."""

    @classmethod
    def define_schema(cls):
        schema = super().define_schema()
        schema.node_id="BlenderInputStringMultiline"
        schema.display_name="Blender Input String Multiline"
        schema.description="Display a string input in the Blender add-on."
        schema.category = "blender"
        schema.inputs.append(io.Custom("GROUP").Input("group", optional=True))
        schema.inputs.append(io.Int.Input("order", default=0, min=MIN_INT, max=MAX_INT, control_after_generate=False, tooltip=TOOLTIP_ORDER))
        schema.inputs.append(io.String.Input("default", default="", tooltip=TOOLTIP_DEFAULT))
        schema.inputs.append(io.Boolean.Input("format_path", default=False, tooltip=TOOLTIP_FORMAT_PATH))
        return schema

    @classmethod
    def execute(cls, value: str, order: int, default: str, format_path: bool, **kwargs) -> io.NodeOutput:
        value = str(os.path.normpath(value)) if format_path else value
        return io.NodeOutput(value)
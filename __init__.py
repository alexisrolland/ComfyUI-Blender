import json
import urllib.parse
from aiohttp import ClientSession, web

from comfy.samplers import KSampler
from server import PromptServer
from .nodes import (
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
    BlenderInputSampler,
    BlenderInputSeed,
    BlenderInputString,
    BlenderInputStringMultiline,
    BlenderOutputDownload3D,
    BlenderOutputSaveGlb,
    BlenderOutputSaveImage,
    BlenderOutputString
)
from .workflow_converter import WorkflowConverter


# Add endpoint to return the list of samplers
@PromptServer.instance.routes.get("/blender/samplers")
async def get_samplers_list(request):
    """Endpoint to get the list of samplers from the ComfyUI server."""

    return web.json_response(KSampler.SAMPLERS)


# Add endpoint to return the list of workflows from the user folder
@PromptServer.instance.routes.get("/blender/workflows")
async def get_workflows_list(request):
    """Endpoint to get the list of workflows in the user folder."""

    # Construct internal URL using the request's host and scheme
    base_url = f"{request.scheme}://{request.host}"
    url = f"{base_url}/v2/userdata?path=workflows"

    # Send request to internal URL
    try:
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    # Parse response and filter to only include files
                    data = json.loads(content)
                    files = [item for item in data if item.get("type") == "file"]
                    return web.json_response(files)
                else:
                    raise web.HTTPNotFound(text="File not found")
    except Exception as e:
        raise web.HTTPInternalServerError(text=f"Error retrieving file: {str(e)}")


# Add endpoint to return a workflow from the user folder in API format
@PromptServer.instance.routes.get("/blender/workflow")
async def get_workflow_file(request):
    """
    Endpoint to get a workflow file from the user folder.
    The query parameter 'filepath' specifies the path to the workflow file as returned by the /blender/workflows endpoint.
    """

    # Get the file path from query parameters
    file_path = request.query.get("filepath", "")
    if not file_path:
        raise web.HTTPBadRequest(text="The filepath query parameter is required")

    # Construct internal URL using the request's host and scheme
    encoded_file_path = urllib.parse.quote(file_path, safe="")
    base_url = f"{request.scheme}://{request.host}"
    url = f"{base_url}/api/userdata/{encoded_file_path}"

    # Send request to internal URL
    try:
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    # Get the workflow content
                    json_data = await response.json()

                    # Check if this is already in API format
                    if WorkflowConverter.is_api_format(json_data):
                        # Return workflow in API format
                        # Format with nice indentation for readability
                        return web.json_response(json_data, dumps=lambda x: json.dumps(x, ensure_ascii=False, indent=2))

                    # Convert to API format
                    if "nodes" in json_data and "links" in json_data:
                        api_format = WorkflowConverter.convert_to_api(json_data)

                        # Return workflow in API format with proper Unicode encoding
                        # Format with nice indentation for readability
                        return web.json_response(api_format, dumps=lambda x: json.dumps(x, ensure_ascii=False, indent=2))
                    else:
                        raise web.HTTPBadRequest(text=f"Invalid JSON: {str(e)}")
                else:
                    raise web.HTTPNotFound(text="File not found")

    except json.JSONDecodeError as e:
        raise web.HTTPBadRequest(text=f"Invalid JSON: {str(e)}")

    except Exception as e:
        raise web.HTTPInternalServerError(text=f"Error retrieving file: {str(e)}")


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
    "BlenderInputSampler": BlenderInputSampler,
    "BlenderInputSeed": BlenderInputSeed,
    "BlenderInputString": BlenderInputString,
    "BlenderInputStringMultiline": BlenderInputStringMultiline,
    "BlenderOutputDownload3D": BlenderOutputDownload3D,
    "BlenderOutputSaveGlb": BlenderOutputSaveGlb,
    "BlenderOutputSaveImage": BlenderOutputSaveImage,
    "BlenderOutputString": BlenderOutputString
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
    "BlenderInputSampler": "Blender Input Sampler",
    "BlenderInputSeed": "Blender Input Seed",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline",
    "BlenderOutputDownload3D": "Blender Output Download 3D",
    "BlenderOutputSaveGlb": "Blender Output Save GLB",
    "BlenderOutputSaveImage": "Blender Output Save Image",
    "BlenderOutputString": "Blender Output String"
}

# Set the web directory to load frontend extensions
WEB_DIRECTORY = "./js"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY"
]
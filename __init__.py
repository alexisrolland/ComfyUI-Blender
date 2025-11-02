import json
import urllib.parse
from aiohttp import ClientSession, web

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
    BlenderOutputSaveImage
)
from .workflow_converter import WorkflowConverter


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
                    return web.Response(text=content, content_type="application/json")
                else:
                    raise web.HTTPNotFound(text="File not found")
    except Exception as e:
        raise web.HTTPInternalServerError(text=f"Error retrieving file: {str(e)}")


# Add endpoint to return the a workflow from the user folder in API format
@PromptServer.instance.routes.get("/blender/workflows/{file_name}")
async def get_workflow_file(request):
    """Endpoint to get a workflow file from the user folder."""

    # Get the file name from the URL
    file_name = request.match_info.get("file_name", "")
    if not file_name:
        raise web.HTTPBadRequest(text="The workflow file name is required")

    # Construct internal URL using the request's host and scheme
    encoded_file_path = urllib.parse.quote(f"workflows/{file_name}", safe="")
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
    "BlenderInputSampler": "Blender Input Sampler",
    "BlenderInputSeed": "Blender Input Seed",
    "BlenderInputString": "Blender Input String",
    "BlenderInputStringMultiline": "Blender Input String Multiline",
    "BlenderOutputDownload3D": "Blender Output Download 3D",
    "BlenderOutputSaveGlb": "Blender Output Save GLB",
    "BlenderOutputSaveImage": "Blender Output Save Image"
}

import bpy
import os
import subprocess
import sys
import uuid

from .operators import import_workflow, run_workflow, select_workflow_folder
from .panels import input_panel, output_panel
from .settings import Settings
from .utils import get_workflow_list, parse_workflow_for_inputs

bl_info = {
    "name": "ComfyUI Blender Plugin",
    "author": "Alexis ROLLAND",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > ComfyUI",
    "description": "Blender plugin to send requests to a ComfyUI server.",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

def install_dependencies():
    """Install required Python dependencies."""
    required_packages = ["websocket-client"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def register():
    # Install dependencies
    install_dependencies()

    # Preferences
    bpy.utils.register_class(Settings)

    # Operators
    import_workflow.register()
    run_workflow.register()
    select_workflow_folder.register()

    # Panels
    input_panel.register()
    output_panel.register()

    # Properties
    bpy.types.Scene.client_id = bpy.props.StringProperty(
        name="Client Id",
        description="Unique identifier for the client",
        default=str(uuid.uuid4())
    )
    bpy.types.Scene.workflow = bpy.props.EnumProperty(
        name="Workflows",
        description="List of workflows to send to the ComfyUI server",
        items=get_workflow_list
    )
    bpy.types.Scene.prompt_id = bpy.props.StringProperty(
        name="Prompt Id",
        description="Unique identifier of the last prompt sent to the ComfyUI server",
        default=""
    )


def unregister():
    # Remove dynamic properties created for workflows inputs
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    workflow_folder = addon_prefs.workflow_folder
    for workflow_file in os.listdir(workflow_folder):
        workflow_path = os.path.join(workflow_folder, workflow_file)
        inputs = parse_workflow_for_inputs(workflow_path)
        for key in inputs.keys():
            delattr(bpy.types.Scene, f"comfy_input_{key}")

    # Properties
    del bpy.types.Scene.client_id
    del bpy.types.Scene.workflow
    del bpy.types.Scene.prompt_id

    # Panels
    input_panel.unregister()
    output_panel.unregister()

    # Operators
    import_workflow.unregister()
    run_workflow.unregister()
    select_workflow_folder.unregister()

    # Preferences
    bpy.utils.unregister_class(Settings)
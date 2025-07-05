import bpy
import json
import os
import subprocess
import sys

from .operators import (
    import_workflow,
    run_workflow,
    select_output_folder,
    select_workflow_folder
)
from .panels import (
    comfyui_panel,
    input_panel,
    output_panel
)
from .settings import Settings
from .utils import get_workflow_list, parse_workflow_for_inputs

bl_info = {
    "name": "ComfyUI Blender",
    "author": "Alexis ROLLAND",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > ComfyUI",
    "description": "Blender plugin to send requests to a ComfyUI server.",
    "warning": "",
    "doc_url": "https://github.com/alexisrolland/ComfyUI-Blender",
    "category": "3D View",
}

# Global variable to manage the WebSocket connection
websocket_connection = None

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
    select_output_folder.register()
    select_workflow_folder.register()

    # Panels
    comfyui_panel.register()
    input_panel.register()
    output_panel.register()

    # Properties
    bpy.types.Scene.workflow = bpy.props.EnumProperty(
        name="Workflow",
        description="Workflow to send to the ComfyUI server",
        items=get_workflow_list
    )
    bpy.types.Scene.queue = bpy.props.IntProperty(
        name="Queue",
        description="Number of workflows in the queue",
        default=0
    )

    class OutputPropertyGroup(bpy.types.PropertyGroup):
        """Property group for outputs."""
        filename: bpy.props.StringProperty(name="filename", description="Filename of the output")
    bpy.utils.register_class(OutputPropertyGroup)
    bpy.types.Scene.output = bpy.props.CollectionProperty(type=OutputPropertyGroup)

def unregister():
    # Remove dynamic properties created for workflows inputs
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    workflow_folder = addon_prefs.workflow_folder
    if os.path.exists(workflow_folder) and os.path.isdir(workflow_folder):
        for workflow_file in os.listdir(workflow_folder):
            workflow_path = os.path.join(workflow_folder, workflow_file)
            with open(workflow_path, "r") as f:
                workflow = json.load(f)
            inputs = parse_workflow_for_inputs(workflow)
            workflow_name = os.path.splitext(os.path.basename(workflow_path))[0]
            for key in inputs.keys():
                attribute_name = f"wkf_{workflow_name}_{key}"
                if hasattr(bpy.types.Scene, attribute_name):
                    delattr(bpy.types.Scene, attribute_name)

    # Preferences
    bpy.utils.unregister_class(Settings)

    # Operators
    import_workflow.unregister()
    run_workflow.unregister()
    select_output_folder.unregister()
    select_workflow_folder.unregister()

    # Panels
    comfyui_panel.unregister()
    input_panel.unregister()
    output_panel.unregister()

    # Properties
    del bpy.types.Scene.workflow
    del bpy.types.Scene.queue
    del bpy.types.Scene.output
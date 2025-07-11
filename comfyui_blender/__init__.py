"""ComfyUI Blender Add-on"""
import subprocess
import sys

from .operators import (
    import_workflow,
    open_file_browser,
    run_workflow,
    select_outputs_folder,
    select_workflows_folder
)
from .panels import (
    input_panel,
    output_panel,
    workflow_panel
)
from . import settings


bl_info = {
    "name": "ComfyUI Blender",
    "author": "Alexis ROLLAND",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > ComfyUI",
    "description": "Blender add-on to send requests to a ComfyUI server.",
    "warning": "",
    "doc_url": "https://github.com/alexisrolland/ComfyUI-Blender",
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
    """Register add-on preferences, operators, and panels."""

    # Install dependencies
    install_dependencies()

    # Preferences
    settings.register()

    # Operators
    import_workflow.register()
    open_file_browser.register()
    run_workflow.register()
    select_outputs_folder.register()
    select_workflows_folder.register()

    # Panels
    workflow_panel.register()
    input_panel.register()
    output_panel.register()

def unregister():
    """Unregister add-on preferences, operators, and panels."""

    # Preferences
    settings.unregister()

    # Operators
    import_workflow.unregister()
    open_file_browser.unregister()
    run_workflow.unregister()
    select_outputs_folder.unregister()
    select_workflows_folder.unregister()

    # Panels
    workflow_panel.unregister()
    input_panel.unregister()
    output_panel.unregister()

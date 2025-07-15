"""ComfyUI Blender Add-on"""
import subprocess
import sys

from .operators import (
    delete_input,
    delete_output,
    import_input,
    import_workflow,
    open_file_browser,
    open_image_editor,
    run_workflow,
    select_folder
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
    "version": (0, 0, 1),
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
    delete_input.register()
    delete_output.register()
    import_input.register()
    import_workflow.register()
    open_file_browser.register()
    open_image_editor.register()
    run_workflow.register()
    select_folder.register()

    # Panels
    workflow_panel.register()
    input_panel.register()
    output_panel.register()

def unregister():
    """Unregister add-on preferences, operators, and panels."""

    # Preferences
    settings.unregister()

    # Operators
    delete_input.unregister()
    delete_output.unregister()
    import_input.unregister()
    import_workflow.unregister()
    open_file_browser.unregister()
    open_image_editor.unregister()
    run_workflow.unregister()
    select_folder.unregister()

    # Panels
    workflow_panel.unregister()
    input_panel.unregister()
    output_panel.unregister()

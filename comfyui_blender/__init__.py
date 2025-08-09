"""ComfyUI Blender Add-on"""
import subprocess
import sys

from .operators import (
    clear_queue,
    delete_input,
    delete_output,
    delete_workflow,
    get_camera_resolution,
    import_3d_model,
    import_image,
    import_workflow,
    lock_seed,
    open_file_browser,
    open_image_editor,
    prepare_3d_model,
    render_depth_map,
    render_lineart,
    render_view,
    run_workflow,
    select_folder,
    set_camera_resolution,
    stop_workflow,
    switch_output_layout
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
    "version": (0, 7, 2),
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > ComfyUI",
    "description": "Blender add-on to send requests to a ComfyUI server.",
    "warning": "",
    "doc_url": "https://github.com/alexisrolland/ComfyUI-Blender",
    "category": "3D View",
}

def register():
    """Register add-on preferences, operators, and panels."""

    # Preferences
    settings.register()

    # Operators
    clear_queue.register()
    delete_input.register()
    delete_output.register()
    delete_workflow.register()
    get_camera_resolution.register()
    import_3d_model.register()
    import_image.register()
    import_workflow.register()
    lock_seed.register()
    open_file_browser.register()
    open_image_editor.register()
    prepare_3d_model.register()
    render_depth_map.register()
    render_lineart.register()
    render_view.register()
    run_workflow.register()
    select_folder.register()
    set_camera_resolution.register()
    stop_workflow.register()
    switch_output_layout.register()

    # Panels
    workflow_panel.register()
    input_panel.register()
    output_panel.register()

def unregister():
    """Unregister add-on preferences, operators, and panels."""

    # Preferences
    settings.unregister()

    # Operators
    clear_queue.unregister()
    delete_input.unregister()
    delete_output.unregister()
    delete_workflow.unregister()
    get_camera_resolution.unregister()
    import_3d_model.unregister()
    import_image.unregister()
    import_workflow.unregister()
    lock_seed.unregister()
    open_file_browser.unregister()
    open_image_editor.unregister()
    prepare_3d_model.unregister()
    render_depth_map.unregister()
    render_lineart.unregister()
    render_view.unregister()
    run_workflow.unregister()
    select_folder.unregister()
    set_camera_resolution.unregister()
    stop_workflow.unregister()
    switch_output_layout.unregister()

    # Panels
    workflow_panel.unregister()
    input_panel.unregister()
    output_panel.unregister()

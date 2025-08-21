"""ComfyUI Blender Add-on"""
from .menus import (
    file_browser_menu
)
from .operators import (
    clear_queue,
    delete_input,
    delete_output,
    delete_workflow,
    download_example_workflows,
    get_camera_resolution,
    import_3d_model,
    import_input_image,
    import_workflow,
    lock_seed,
    open_file_browser,
    open_image_editor,
    open_image,
    prepare_glb_file,
    prepare_obj_file,
    rename_workflow,
    render_depth_map,
    render_lineart,
    render_view,
    run_workflow,
    select_folder,
    set_camera_resolution,
    show_error_popup,
    stop_workflow,
    switch_output_layout
)
from .panels import (
    file_browser_panel,
    input_panel,
    output_panel,
    workflow_panel
)
from . import hooks
from . import settings


bl_info = {
    "name": "ComfyUI Blender",
    "author": "Alexis ROLLAND",
    "version": (0, 13, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > ComfyUI",
    "description": "Blender add-on to send requests to a ComfyUI server.",
    "warning": "",
    "doc_url": "https://github.com/alexisrolland/ComfyUI-Blender",
    "category": "3D View",
}

def register():
    """Register add-on preferences, operators, and panels."""

    # Hooks
    hooks.register()

    # Preferences
    settings.register()

    # Menus
    file_browser_menu.register()

    # Operators
    clear_queue.register()
    delete_input.register()
    delete_output.register()
    delete_workflow.register()
    download_example_workflows.register()
    get_camera_resolution.register()
    import_3d_model.register()
    import_input_image.register()
    import_workflow.register()
    lock_seed.register()
    open_file_browser.register()
    open_image_editor.register()
    open_image.register()
    prepare_glb_file.register()
    prepare_obj_file.register()
    rename_workflow.register()
    render_depth_map.register()
    render_lineart.register()
    render_view.register()
    run_workflow.register()
    select_folder.register()
    set_camera_resolution.register()
    show_error_popup.register()
    stop_workflow.register()
    switch_output_layout.register()

    # Panels
    file_browser_panel.register()
    workflow_panel.register()
    input_panel.register()
    output_panel.register()

def unregister():
    """Unregister add-on preferences, operators, and panels."""

    # Hooks
    hooks.register()

    # Preferences
    settings.unregister()

    # Menus
    file_browser_menu.unregister()

    # Operators
    clear_queue.unregister()
    delete_input.unregister()
    delete_output.unregister()
    delete_workflow.unregister()
    download_example_workflows.unregister()
    get_camera_resolution.unregister()
    import_3d_model.unregister()
    import_input_image.unregister()
    import_workflow.unregister()
    lock_seed.unregister()
    open_file_browser.unregister()
    open_image_editor.unregister()
    open_image.unregister()
    prepare_glb_file.unregister()
    prepare_obj_file.unregister()
    rename_workflow.unregister()
    render_depth_map.unregister()
    render_lineart.unregister()
    render_view.unregister()
    run_workflow.unregister()
    select_folder.unregister()
    set_camera_resolution.unregister()
    show_error_popup.unregister()
    stop_workflow.unregister()
    switch_output_layout.unregister()

    # Panels
    file_browser_panel.unregister()
    workflow_panel.unregister()
    input_panel.unregister()
    output_panel.unregister()

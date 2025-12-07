"""ComfyUI Blender Add-on"""
from .menus import (
    connection_menu,
    file_browser_menu,
    output_menu
)
from .operators import (
    clear_queue,
    connect_to_server,
    create_material,
    delete_input,
    delete_output,
    delete_workflow,
    disconnect_from_server,
    download_workflows,
    get_camera_resolution,
    get_random_seed,
    import_3d_model,
    import_image,
    import_workflow,
    open_file_browser,
    open_image_editor,
    open_image,
    open_text_editor,
    prepare_glb_file,
    prepare_obj_file,
    project_material,
    rename_workflow,
    render_depth_map,
    render_lineart,
    render_view,
    reset_folder,
    run_workflow,
    select_brush,
    select_folder,
    send_to_input,
    set_camera_resolution,
    show_connection_menu,
    show_error_popup,
    show_output_menu,
    stop_workflow,
    switch_output_layout,
    upload_input_image
)
from .panels import (
    file_browser_panel,
    input_panel,
    output_panel,
    paint_panel,
    workflow_panel
)
from . import hooks
from . import settings
from .connection import disconnect


bl_info = {
    "name": "ComfyUI Blender",
    "author": "Alexis ROLLAND",
    "version": (4, 1, 1),
    "blender": (5, 0, 0),
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
    connection_menu.register()
    file_browser_menu.register()
    output_menu.register()

    # Operators
    clear_queue.register()
    connect_to_server.register()
    create_material.register()
    delete_input.register()
    delete_output.register()
    delete_workflow.register()
    disconnect_from_server.register()
    download_workflows.register()
    get_camera_resolution.register()
    get_random_seed.register()
    import_3d_model.register()
    import_image.register()
    import_workflow.register()
    open_file_browser.register()
    open_image_editor.register()
    open_image.register()
    open_text_editor.register()
    prepare_glb_file.register()
    prepare_obj_file.register()
    project_material.register()
    rename_workflow.register()
    render_depth_map.register()
    render_lineart.register()
    render_view.register()
    reset_folder.register()
    run_workflow.register()
    select_brush.register()
    select_folder.register()
    send_to_input.register()
    set_camera_resolution.register()
    show_connection_menu.register()
    show_error_popup.register()
    show_output_menu.register()
    stop_workflow.register()
    switch_output_layout.register()
    upload_input_image.register()

    # Panels
    file_browser_panel.register()
    workflow_panel.register()
    input_panel.register()
    output_panel.register()
    paint_panel.register()


def unregister():
    """Unregister add-on preferences, operators, and panels."""

    # Ensure WebSocket connection is closed and listening thread is stopped
    disconnect()

    # Hooks
    hooks.register()

    # Preferences
    settings.unregister()

    # Menus
    connection_menu.unregister()
    file_browser_menu.unregister()
    output_menu.unregister()

    # Operators
    clear_queue.unregister()
    connect_to_server.unregister()
    create_material.unregister()
    delete_input.unregister()
    delete_output.unregister()
    delete_workflow.unregister()
    disconnect_from_server.unregister()
    download_workflows.unregister()
    get_camera_resolution.unregister()
    get_random_seed.unregister()
    import_3d_model.unregister()
    import_image.unregister()
    import_workflow.unregister()
    open_file_browser.unregister()
    open_image_editor.unregister()
    open_image.unregister()
    open_text_editor.unregister()
    prepare_glb_file.unregister()
    prepare_obj_file.unregister()
    project_material.unregister()
    rename_workflow.unregister()
    render_depth_map.unregister()
    render_lineart.unregister()
    render_view.unregister()
    reset_folder.unregister()
    run_workflow.unregister()
    select_brush.unregister()
    select_folder.unregister()
    send_to_input.unregister()
    set_camera_resolution.unregister()
    show_connection_menu.unregister()
    show_error_popup.unregister()
    show_output_menu.unregister()
    stop_workflow.unregister()
    switch_output_layout.unregister()
    upload_input_image.unregister()

    # Panels
    file_browser_panel.unregister()
    workflow_panel.unregister()
    input_panel.unregister()
    output_panel.unregister()
    paint_panel.unregister()
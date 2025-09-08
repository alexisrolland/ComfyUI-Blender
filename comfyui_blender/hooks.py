import logging
import os

import bpy
from bpy.app.handlers import persistent

from .connection import disconnect

log = logging.getLogger("comfyui_blender")


@persistent
def load_pre_handler(scene, depsgraph):
    """Called before a blend file is loaded"""

    # Ensure previous connection is closed and listening thread is stopped
    disconnect()


@persistent
def load_post_handler(scene, depsgraph):
    """Called after loading the blend file"""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    project_settings = bpy.context.scene.comfyui_project_settings

    # Update the base folder according to the .blend file location
    if bpy.data.filepath and project_settings.use_blend_file_location:
        addon_prefs.base_folder = os.path.dirname(bpy.data.filepath)
    else:
        # Reset base folder if the .blend file location is empty
        project_settings.use_blend_file_location = False
        base_path = os.path.dirname(bpy.utils.resource_path("USER"))
        base_path = os.path.join(base_path, "data", __package__)
        addon_prefs.base_folder = base_path

    # Force the update of the workflow property to refresh the input panel
    if addon_prefs.workflow:
        addon_prefs.workflow = addon_prefs.workflow


@persistent
def save_post_handler(scene, depsgraph):
    """Called after saving the blend file"""

    # Update the base folder according to the .blend file location
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    project_settings = bpy.context.scene.comfyui_project_settings
    if project_settings.use_blend_file_location:
        addon_prefs.base_folder = os.path.dirname(bpy.data.filepath)


def register():
    """Register handlers."""

    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.save_post.append(save_post_handler)

def unregister():
    """Unregister handlers."""

    if disconnect in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(load_pre_handler)

    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)

    if save_post_handler in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(save_post_handler)

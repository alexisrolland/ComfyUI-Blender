"""ComfyUI Blender Add-on Settings"""
import os
import uuid

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty
)

from .workflow import get_workflow_list, register_workflow_class


class ComfyBlenderSettings(bpy.types.AddonPreferences):
    """ComfyUI Blender Add-on Preferences"""

    # The bl_idname must match the addon name
    # The addon name is the folder name where this file is located
    bl_idname = "comfyui_blender"

    # Client Id used to identify the Blender add-on instance
    # This is used when connecting to the ComfyUI server via WebSocket
    client_id: StringProperty(
        name="Client Id",
        description="Unique identifier of your Blender add-on",
        default=str(uuid.uuid4())
    )

    # ComfyUI server address
    server_address: StringProperty(
        name="Server Address",
        description="URL of the ComfyUI server",
        default="http://127.0.0.1:8188"
    )

    # Connection status
    # This is used to indicate if the Blender add-on is connected to the ComfyUI server via WebSocket
    connection_status: BoolProperty(
        name="Connection Status",
        description="Indicate if the Blender add-on is connected to the ComfyUI server",
        default=False
    )

    # Construct base folders path
    blender_version = bpy.app.version
    major, minor, patch = blender_version
    addon_name = __package__

    # Workflows folder
    default_workflows_folder = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Blender Foundation\\Blender\\{major}.{minor}\\scripts\\addons\\{addon_name}\\workflows"
    os.makedirs(default_workflows_folder, exist_ok=True)
    workflows_folder: StringProperty(
        name="Workflows Folder",
        description="Folder where workflows are stored",
        default=default_workflows_folder
    )

    # Outputs folder path
    default_outputs_folder = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Blender Foundation\\Blender\\{major}.{minor}\\scripts\\addons\\{addon_name}\\outputs"
    os.makedirs(default_outputs_folder, exist_ok=True)
    outputs_folder: StringProperty(
        name="Outputs Folder",
        description="Folder where outputs are stored",
        default=default_outputs_folder
    )

    # Workflow
    workflow: EnumProperty(
        name="Workflow",
        description="Workflow to send to the ComfyUI server",
        items=get_workflow_list,
        update=register_workflow_class
    )

    # Queue
    queue: IntProperty(
        name="Queue",
        description="Number of workflows in the queue",
        default=0
    )

    # Outputs collection
    # Declare an output property group used in a collection
    class OutputPropertyGroup(bpy.types.PropertyGroup):
        """Property group for outputs collection."""

        filename: StringProperty(
            name="File Name",
            description="File name of the output"
        )
        filepath: StringProperty(
            name="File Path",
            description="Relative file path of the output"
        )
        type: EnumProperty(
            name="Type",
            description="Type of the output",
            items=[("image", "Image", "Image output")]
        )
    bpy.utils.register_class(OutputPropertyGroup)
    outputs_collection: CollectionProperty(
        name="Outputs Collection",
        description="Collection of generated outputs",
        type=OutputPropertyGroup
    )

    def draw(self, context):
        """Draw the panel."""

        layout = self.layout

        # Client Id and server address
        col = layout.column()
        col.label(text="Server:")
        col.prop(self, "client_id", emboss=False)
        col.prop(self, "server_address")

        # Workflows folder
        col = layout.column()
        col.label(text="Folders:")
        row = col.split(factor=0.8)
        row.prop(self, "workflows_folder", text="Workflows Folder")
        row.operator("comfy.select_workflows_folder", text="Select")

        # Outputs folder
        row = col.split(factor=0.8)
        row.prop(self, "outputs_folder", text="Outputs Folder")
        row.operator("comfy.select_outputs_folder", text="Select")

def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderSettings)

    # Force the update of the workflow property to trigger the registration of the selected workflow class
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.workflow = addon_prefs.workflow

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderSettings)

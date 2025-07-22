"""ComfyUI Blender Add-on Settings"""
import os
import uuid

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    StringProperty
)

from .connection import disconnect
from .workflow import get_workflow_list, register_workflow_class


def update_progress(self, context):
    """Update callback to force UI redraw when progress changes."""

    if context.screen:
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

def update_server_address(self, context):
    """Reset connection and cleanse the server address."""

    # Reset current connection
    disconnect()

    # Ensure the server address ends without a slash.
    while self.server_address.endswith("/"):
        self.server_address = self.server_address.rstrip("/")

class PromptPropertyGroup(bpy.types.PropertyGroup):
    """Property group for the queue collection."""

    # The name property serves as the key for the collection
    name: StringProperty(
        name="Prompt Id",
        description="Identifier of the prompt returned by the ComfyUI server"
    )
    workflow: StringProperty(
        name="Workflow",
        description="Workflow sent to the ComfyUI server"
    )
    outputs: StringProperty(
        name="Outputs",
        description="Output nodes of the workflow"
    )

class OutputPropertyGroup(bpy.types.PropertyGroup):
    """Property group for outputs collection."""

    # The name property serves as the key for the collection
    # Because the file path is unique, we use it as the key
    name: StringProperty(
        name="File Path",
        description="Relative file path of the output"
    )
    filename: StringProperty(
        name="File Name",
        description="File name of the output"
    )
    type: EnumProperty(
        name="Type",
        description="Type of the output",
        items=[("3d", "3d", "3D model output"), ("image", "Image", "Image output")]
    )

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
        default="http://127.0.0.1:8188",
        update=update_server_address
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
    base_path = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Blender Foundation\\Blender\\{major}.{minor}\\scripts\\addons\\{addon_name}"

    # Workflows folder
    default_workflows_folder = os.path.join(base_path, "workflows")
    os.makedirs(default_workflows_folder, exist_ok=True)
    workflows_folder: StringProperty(
        name="Workflows Folder",
        description="Folder where workflows are stored",
        default=default_workflows_folder
    )

    # Inputs folder path
    default_inputs_folder = os.path.join(base_path, "inputs")
    os.makedirs(default_inputs_folder, exist_ok=True)
    inputs_folder: StringProperty(
        name="Inputs Folder",
        description="Folder where inputs are stored",
        default=default_inputs_folder
    )

    # Outputs folder path
    default_outputs_folder = os.path.join(base_path, "outputs")
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

    # Lock seed
    lock_seed: BoolProperty(
        name="Lock Seed",
        description="Lock the seed value used to initialize generation",
        default=False
    )

    # Queue
    queue: CollectionProperty(
        name="Queue",
        description="Collection of prompts sent to the ComfyUI server",
        type=PromptPropertyGroup
    )

    # Progress value used for the progress bar
    progress_value: bpy.props.FloatProperty(
        name="Progress",
        description="Generation progress",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        update=update_progress
    )

    # Outputs
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
        select_workflows_folder = row.operator("comfy.select_folder", text="Select")
        select_workflows_folder.target_property = "workflows_folder"

        # Inputs folder
        row = col.split(factor=0.8)
        row.prop(self, "inputs_folder", text="Inputs Folder")
        select_inputs_folder = row.operator("comfy.select_folder", text="Select")
        select_inputs_folder.target_property = "inputs_folder"

        # Outputs folder
        row = col.split(factor=0.8)
        row.prop(self, "outputs_folder", text="Outputs Folder")
        select_outputs_folder = row.operator("comfy.select_folder", text="Select")
        select_outputs_folder.target_property = "outputs_folder"


def register():
    """Register the operator."""

    bpy.utils.register_class(PromptPropertyGroup)
    bpy.utils.register_class(OutputPropertyGroup)
    bpy.utils.register_class(ComfyBlenderSettings)

    # Force the update of the workflow property to trigger the registration of the selected workflow class
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.workflow = addon_prefs.workflow

def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(PromptPropertyGroup)
    bpy.utils.unregister_class(OutputPropertyGroup)
    bpy.utils.unregister_class(ComfyBlenderSettings)

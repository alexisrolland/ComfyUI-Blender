"""ComfyUI Blender Add-on Settings"""

import logging
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
from .utils import show_error_popup
from .workflow import get_workflow_list, register_workflow_class

log = logging.getLogger("comfyui_blender")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())


def update_progress(self, context):
    """Callback to force UI redraw when progress changes."""

    if context.screen:
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

def update_project_folders(self, context):
    """Callback to update workflows, inputs and outputs folders according to the project base folder."""

    # Set workflows folder
    workflows_folder = os.path.join(self.base_folder, "workflows")
    os.makedirs(workflows_folder, exist_ok=True)
    self.workflows_folder = workflows_folder

    # Set inputs folder
    inputs_folder = os.path.join(self.base_folder, "inputs")
    os.makedirs(inputs_folder, exist_ok=True)
    self.inputs_folder = inputs_folder

    # Set outputs folder
    outputs_folder = os.path.join(self.base_folder, "outputs")
    os.makedirs(outputs_folder, exist_ok=True)
    self.outputs_folder = outputs_folder

def update_server_address(self, context):
    """Reset connection and cleanse the server address."""

    # Reset current connection
    disconnect()

    # Ensure the server address ends without a slash.
    while self.server_address.endswith("/"):
        self.server_address = self.server_address.rstrip("/")


def toggle_debug_logging(self, context):
    if self.debug_logging:
        log.setLevel(logging.DEBUG)
        log.debug("Debug logging activated.")
    else:
        log.setLevel(logging.INFO)


def update_use_blend_file_location(self, context):
    """Update project base folders according to the location of the .blend file."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences

    # Set project folder to the current .blend file location
    if self.use_blend_file_location:
        if bpy.data.filepath:
            addon_prefs.base_folder = os.path.dirname(bpy.data.filepath)
        else:
            self.use_blend_file_location = False
            show_error_popup("Save your .blend file before using this option.")
            return
    else:
        # Reset to the default base folder
        addon_prefs.base_folder = addon_prefs.base_path

    # Update workflows, inputs and outputs folders
    update_project_folders(addon_prefs, context)

    # Force the update of the workflow property to refresh the input panel
    addon_prefs.workflow = addon_prefs.workflow

class ProjectSettingsPropertyGroup(bpy.types.PropertyGroup):
    """Property group for project-specific settings."""

    use_blend_file_location: BoolProperty(
        name="Use .blend File Location",
        description="Save workflows, inputs and outputs in the same folder as the current .blend file instead of the add-on data folder.",
        default=False,
        update=update_use_blend_file_location
    )

class PromptPropertyGroup(bpy.types.PropertyGroup):
    """Property group for the queue collection."""

    # The name property serves as the key for the collection
    name: StringProperty(
        name="Prompt Id",
        description="Identifier of the prompt returned by the ComfyUI server."
    )
    workflow: StringProperty(
        name="Workflow",
        description="Workflow sent to the ComfyUI server."
    )
    outputs: StringProperty(
        name="Outputs",
        description="Output nodes of the workflow."
    )
    status: EnumProperty(
        name="Status",
        description="Status of the workflow in the queue.",
        default="pending",
        items=[
            ("pending", "Pending", ""),
            ("execution_start", "Execution Start", ""),
            ("execution_cached", "Execution Cached", ""),
            ("executing", "Executing", ""),
            ("executed", "Executed", "")
        ]
    )

class OutputPropertyGroup(bpy.types.PropertyGroup):
    """Property group for outputs collection."""

    # The name property serves as the key for the collection
    # Because the file path is unique, we use it as the key
    name: StringProperty(
        name="File Path",
        description="Relative file path of the output."
    )
    filename: StringProperty(
        name="File Name",
        description="File name of the output."
    )
    type: EnumProperty(
        name="Type",
        description="Type of the output.",
        items=[("3d", "3D", "3D model output"), ("image", "Image", "Image output")]
    )

class AddonPreferences(bpy.types.AddonPreferences):
    """Add-on Preferences"""

    # The bl_idname must match the addon name
    # The addon name is the folder name where this file is located
    bl_idname = "comfyui_blender"

    # Client Id used to identify the Blender add-on instance
    # This is used when connecting to the ComfyUI server via WebSocket
    client_id: StringProperty(
        name="Client Id",
        description="Unique identifier of your Blender add-on.",
        default=str(uuid.uuid4())
    )

    # ComfyUI server address
    server_address: StringProperty(
        name="Server Address",
        description="URL of the ComfyUI server.",
        default="http://127.0.0.1:8188",
        update=update_server_address
    )

    # Toggle debug logging
    debug_logging: BoolProperty(
        name="Debug logging",
        description="Activate debug logs for the addon.",
        default=False,
        update=toggle_debug_logging
    )
    # Connection status
    # This is used to indicate if the Blender add-on is connected to the ComfyUI server via WebSocket
    connection_status: BoolProperty(
        name="Connection Status",
        description="Indicate if the Blender add-on is connected to the ComfyUI server.",
        default=False
    )

    # Construct base folders path
    base_path = os.path.dirname(bpy.utils.resource_path("USER"))
    base_path = os.path.join(base_path, "data", __package__)

    # Project base folder
    base_folder: StringProperty(
        name="Base Folder",
        description="Base project folder where workflows, inputs and outputs are stored.",
        default=base_path,
        update=update_project_folders
    )

    # Workflows folder
    default_workflows_folder = os.path.join(base_path, "workflows")
    os.makedirs(default_workflows_folder, exist_ok=True)
    workflows_folder: StringProperty(
        name="Workflows Folder",
        description="Folder where workflows are stored.",
        default=default_workflows_folder
    )

    # Inputs folder path
    default_inputs_folder = os.path.join(base_path, "inputs")
    os.makedirs(default_inputs_folder, exist_ok=True)
    inputs_folder: StringProperty(
        name="Inputs Folder",
        description="Folder where inputs are stored.",
        default=default_inputs_folder
    )

    # Outputs folder path
    default_outputs_folder = os.path.join(base_path, "outputs")
    os.makedirs(default_outputs_folder, exist_ok=True)
    outputs_folder: StringProperty(
        name="Outputs Folder",
        description="Folder where outputs are stored.",
        default=default_outputs_folder
    )

    # Current workflow
    workflow: EnumProperty(
        name="Workflow",
        description="Workflow to send to the ComfyUI server.",
        items=get_workflow_list,
        update=register_workflow_class
    )

    # Lock seed
    lock_seed: BoolProperty(
        name="Lock Seed",
        description="Lock the seed value used to initialize generation.",
        default=False
    )

    # Queue
    queue: CollectionProperty(
        name="Queue",
        description="Collection of prompts sent to the ComfyUI server.",
        type=PromptPropertyGroup
    )

    # Progress value used for the progress bar
    progress_value: bpy.props.FloatProperty(
        name="Progress",
        description="Generation progress.",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        update=update_progress
    )

    # Outputs
    outputs_collection: CollectionProperty(
        name="Outputs Collection",
        description="Collection of generated outputs.",
        type=OutputPropertyGroup
    )

    # Outputs layout
    outputs_layout: EnumProperty(
        name="Outputs Layout",
        description="Layout type for the outputs.",
        default="thumbnail",
        items=[("list", "List", "Display outputs in a list"), ("thumbnail", "Thumbnail", "Display outputs as thumbnails")],
    )

    def draw(self, context):
        """Draw the panel."""

        layout = self.layout

        # Client Id and server address
        layout.label(text="Server:")
        layout.prop(self, "client_id")
        layout.prop(self, "server_address")
        layout.prop(self, "debug_logging")

        # Folders
        layout.label(text="Folders:")

        # Get project settings
        project_settings = bpy.context.scene.comfyui_project_settings
        use_file_loc = project_settings.use_blend_file_location

        # Base folder
        row = layout.row(align=True)
        row.prop(self, "base_folder", text="Base Folder", emboss=not use_file_loc)
        if not use_file_loc:
            select_base_folder = row.operator("comfy.select_folder", text="", icon="FILE_FOLDER")
            select_base_folder.target_property = "base_folder"

        # Create box for subfolders
        box = layout.box()
        col = box.column(align=True)

        # Inputs folder
        row = col.row(align=True)
        row.prop(self, "inputs_folder", text="Inputs", emboss=not use_file_loc)
        if not use_file_loc:
            select_inputs_folder = row.operator("comfy.select_folder", text="", icon="FILE_FOLDER")
            select_inputs_folder.target_property = "inputs_folder"

        # Outputs folder
        row = col.row(align=True)
        row.prop(self, "outputs_folder", text="Outputs", emboss=not use_file_loc)
        if not use_file_loc:
            select_outputs_folder = row.operator("comfy.select_folder", text="", icon="FILE_FOLDER")
            select_outputs_folder.target_property = "outputs_folder"
        
        # Workflows folder
        row = col.row(align=True)
        row.prop(self, "workflows_folder", text="Workflows", emboss=not use_file_loc)
        if not use_file_loc:
            select_workflows_folder = row.operator("comfy.select_folder", text="", icon="FILE_FOLDER")
            select_workflows_folder.target_property = "workflows_folder"

def register():
    """Register classes."""

    bpy.utils.register_class(ProjectSettingsPropertyGroup)
    bpy.utils.register_class(PromptPropertyGroup)
    bpy.utils.register_class(OutputPropertyGroup)
    bpy.utils.register_class(AddonPreferences)

    # Force the update of the workflow property to trigger the registration of the selected workflow class
    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    addon_prefs.workflow = addon_prefs.workflow

    # Register the project settings to the scene
    bpy.types.Scene.comfyui_project_settings = bpy.props.PointerProperty(type=ProjectSettingsPropertyGroup)

def unregister():
    """Unregister classes."""

    bpy.utils.unregister_class(ProjectSettingsPropertyGroup)
    bpy.utils.unregister_class(PromptPropertyGroup)
    bpy.utils.unregister_class(OutputPropertyGroup)
    bpy.utils.unregister_class(AddonPreferences)

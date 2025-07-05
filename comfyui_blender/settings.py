import bpy
import os
import uuid

class Settings(bpy.types.AddonPreferences):
    # The bl_idname must match the addon name
    # The addon name is the folder name where this file is located
    bl_idname = "comfyui_blender"

    client_id: bpy.props.StringProperty(
        name="Client Id",
        description="Unique identifier of your Blender plugin",
        default=str(uuid.uuid4())
    )

    server_address: bpy.props.StringProperty(
        name="Server Address",
        description="URL of the ComfyUI server",
        default="http://127.0.0.1:8188"
    )

    connection_status: bpy.props.BoolProperty(
        name="Connection Status",
        description="Indicate if the Blender plugin is connected to the ComfyUI server",
        default=False
    )

    # Construct base folders path
    blender_version = bpy.app.version
    major, minor, patch = blender_version
    addon_name = __package__

    # Workflows folder path
    default_workflow_folder = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Blender Foundation\\Blender\\{major}.{minor}\\scripts\\addons\\{addon_name}\\workflows"
    os.makedirs(default_workflow_folder, exist_ok=True)
    workflow_folder: bpy.props.StringProperty(
        name="Workflows Folder",
        description="Folder where workflows are stored",
        default=default_workflow_folder
    )

    # Outputs folder path
    default_output_folder = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Blender Foundation\\Blender\\{major}.{minor}\\scripts\\addons\\{addon_name}\\outputs"
    os.makedirs(default_output_folder, exist_ok=True)
    output_folder: bpy.props.StringProperty(
        name="Outputs Folder",
        description="Folder where outputs are stored",
        default=default_output_folder
    )

    def draw(self, context):
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
        row.prop(self, "workflow_folder", text="Workflows Folder")
        row.operator("comfy.select_workflow_folder", text="Select")

        # Outputs folder
        row = col.split(factor=0.8)
        row.prop(self, "output_folder", text="Outputs Folder")
        row.operator("comfy.select_output_folder", text="Select")
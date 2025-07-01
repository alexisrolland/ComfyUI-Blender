import bpy
import os

class Settings(bpy.types.AddonPreferences):
    # The bl_idname must match the addon name ()
    # The addon name is the folder name where this file is located
    bl_idname = "comfyui_blender"

    server_address: bpy.props.StringProperty(
        name="Server Address",
        description="URL of the ComfyUI server",
        default="http://127.0.0.1:8188"
    )
    server_connection_status: bpy.props.BoolProperty(
        name="Connection Status",
        description="Indicate if the plugin is connected to the ComfyUI server",
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

        # Server address
        col = layout.column(align=True)
        col.prop(self, "server_address")

        # Connection status
        row = col.row(align=True)
        row.label(text="Server Status:")
        if self.server_connection_status:
           row.label(text="Connected", icon="LINKED")
        else:
           row.label(text="Disconnected", icon="UNLINKED")

        # Buttons to connect to the server
        row = layout.row()
        row.operator("comfy.connect_to_server", text="Connect to Server")
        row.operator("comfy.disconnect_from_server", text="Disconnect from Server")

        # Workflows folder
        col = layout.column(align=True)
        row = col.split(factor=0.8, align=True)
        row.prop(self, "workflow_folder", text="Workflows Folder")
        row.operator("comfy.select_workflow_folder", text="Select")

        # Outputs folder
        row = col.split(factor=0.8, align=True)
        row.prop(self, "output_folder", text="Outputs Folder")
        row.operator("comfy.select_output_folder", text="Select")
import bpy
import os

class Settings(bpy.types.AddonPreferences):
    # The bl_idname must match the addon name ()
    # The addon name is the folder name where this file is located
    bl_idname = "comfyui_blender_plugin"

    server_address: bpy.props.StringProperty(
        name="Server Address",
        description="URL of the ComfyUI server",
        default="http://127.0.0.1:8188"
    )

    # Construct the workflows folder path
    blender_version = bpy.app.version
    major, minor, patch = blender_version
    addon_name = __package__
    default_workflow_folder = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Blender Foundation\\Blender\\{major}.{minor}\\scripts\\addons\\{addon_name}\\workflows"
    os.makedirs(default_workflow_folder, exist_ok=True)

    workflow_folder: bpy.props.StringProperty(
        name="Workflows Folder",
        description="Folder where workflows are stored",
        default=default_workflow_folder
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "server_address")
        layout.prop(self, "workflow_folder")
        layout.operator("comfy.select_workflow_folder", text="Select Folder")
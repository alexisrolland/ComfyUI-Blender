import bpy
import os
import shutil
from ..utils import parse_workflow_for_inputs, create_dynamic_properties

class COMFY_OT_ImportWorkflow(bpy.types.Operator):
    """Operator to import a workflow JSON file."""
    bl_idname = "comfy.import_workflow"
    bl_label = "Import Workflow"
    bl_description = "Import a workflow JSON file"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath.endswith(".json"):
            # Get the workflows folder from addon preferences
            addon_prefs = context.preferences.addons["comfyui_blender_plugin"].preferences
            workflow_folder = addon_prefs.workflow_folder

            # Create the workflows folder if it doesn't exist
            os.makedirs(workflow_folder, exist_ok=True)
            base_name = os.path.basename(self.filepath)
            destination = os.path.join(workflow_folder, base_name)

            # Handle file name conflicts by appending an incremental number
            if os.path.exists(destination):
                name, ext = os.path.splitext(base_name)
                counter = 1
                while os.path.exists(os.path.join(workflow_folder, f"{name}_{counter}{ext}")):
                    counter += 1
                destination = os.path.join(workflow_folder, f"{name}_{counter}{ext}")

            # Copy the file to the workflows directory
            try:
                shutil.copy(self.filepath, destination)
                self.report({'INFO'}, f"Workflow copied to: {destination}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to copy workflow: {e}")
            
            # Create dynamic properties for the imported workflow
            workflow_name = os.path.splitext(base_name)[0]
            inputs = parse_workflow_for_inputs(destination)
            create_dynamic_properties(workflow_name, inputs)
        else:
            self.report({'ERROR'}, "Selected file is not a JSON file.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(COMFY_OT_ImportWorkflow)

def unregister():
    bpy.utils.unregister_class(COMFY_OT_ImportWorkflow)
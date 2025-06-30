import bpy
import os
from ..utils import parse_workflow_for_inputs

class COMFY_PT_InputPanel(bpy.types.Panel):
    bl_label = "Inputs"
    bl_idname = "COMFY_PT_InputPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw(self, context):
        layout = self.layout

        # Button to import workflows
        layout.operator("comfy.import_workflow", text="Import Workflow")

        # Dropdown list of workflows
        layout.prop(context.scene, "workflow")

        # Parse the selected workflow and add inputs
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        workflow_folder = addon_prefs.workflow_folder
        selected_workflow = context.scene.workflow
        workflow_path = os.path.join(workflow_folder, selected_workflow)
        if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
            box = layout.box()
            workflow_name = os.path.splitext(os.path.basename(workflow_path))[0]
            inputs = parse_workflow_for_inputs(workflow_path)

            # Create panel properties for each input
            for key in inputs.keys():
                box.prop(context.scene, f"wkf_{workflow_name}_{key}")

            # Button to run the selected workflow
            box.operator("comfy.run_workflow", text="Run Workflow")

def register():
    bpy.utils.register_class(COMFY_PT_InputPanel)

def unregister():
    bpy.utils.unregister_class(COMFY_PT_InputPanel)
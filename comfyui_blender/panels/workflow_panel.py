"""Panel to display workflows."""
import os

import bpy


class ComfyBlenderPanelWorkflowBase(bpy.types.Panel):
    """Panel to display workflows options."""

    bl_label = "Workflow"
    bl_region_type = "UI"
    bl_category = "ComfyUI"

    def draw_header(self, context):
        """Draw the panel header."""

        layout = self.layout
        layout.label(icon="NODETREE")

    def draw(self, context):
        """Draw the panel."""

        # Use .blend file location
        row = self.layout.row(align=True)
        project_settings = bpy.context.scene.comfyui_project_settings
        row.prop(project_settings, "use_blend_file_location")

        # Buttons to connect to server
        addon_prefs = context.preferences.addons["comfyui_blender"].preferences
        if addon_prefs.connection_status:
            row.operator("comfy.show_connection_menu", text="Connected", icon="INTERNET")
        else:
            row.operator("comfy.show_connection_menu", text="Disconnected", icon="INTERNET_OFFLINE")

        # Buttons to open preferences
        row.operator("preferences.addon_show", text="", icon="PREFERENCES").module = "comfyui_blender"

        # Get workflows information
        workflows_folder = str(addon_prefs.workflows_folder)
        workflow_filename = str(addon_prefs.workflow)
        workflow_path = os.path.join(workflows_folder, workflow_filename)

        # Button to import workflows
        row = self.layout.row(align=True)
        import_workflow = row.operator("comfy.import_workflow", text="Import Workflow")
        import_workflow.invoke_default = True

        # Button to download example workflows
        # Hide this since example workflows are likely not working natively on the user's ComfyUI instance
        # row.operator("comfy.download_example_workflows", text="", icon="IMPORT")

        # Button to open the workflows folder
        file_browser = row.operator("comfy.open_file_browser", text="", icon="FILE_FOLDER")
        file_browser.folder_path = workflows_folder
        file_browser.custom_label = "Open Workflows Folder"

        # Dropdown list of workflows
        row = self.layout.row(align=True)
        row.prop(addon_prefs, "workflow")

        # Get current workflow
        workflow = getattr(addon_prefs, "workflow")
        row = row.row(align=True)
        row.enabled = True if workflow != "none" else False

        # Button to rename the current workflow
        rename_workflow = row.operator("comfy.rename_workflow", text="", icon="GREASEPENCIL")
        rename_workflow.current_filename = workflow_filename
        rename_workflow.new_filename = workflow_filename

        # Button to delete the current workflow
        delete_workflow = row.operator("comfy.delete_workflow", text="", icon="TRASH")
        delete_workflow.filename = workflow_filename
        delete_workflow.filepath = workflow_path

        # Queue status and progress bar
        row = self.layout.row(align=True)
        split = row.split(factor=0.21)
        split.label(text=f"Queue: {len(addon_prefs.queue)}")
        sub_row = split.row(align=True)
        sub_row.progress(factor=addon_prefs.progress_value, text=f"{int(addon_prefs.progress_value * 100)}%", type="BAR")
        sub_row.operator("comfy.stop_workflow", text="", icon="CANCEL")
        sub_row.operator("comfy.clear_queue", text="", icon="SEQ_SEQUENCER")


class ComfyBlenderPanelWorkflow3DViewer(ComfyBlenderPanelWorkflowBase, bpy.types.Panel):
    """Class to display the panel in the 3D viewer."""

    bl_idname = "COMFY_PT_Workflow_3DViewer"
    bl_space_type = "VIEW_3D"


class ComfyBlenderPanelWorkflowImageEditor(ComfyBlenderPanelWorkflowBase, bpy.types.Panel):
    """Class to display the panel in the image editor."""

    bl_idname = "COMFY_PT_Workflow_ImageEditor"
    bl_space_type = "IMAGE_EDITOR"

def register():
    """Register the panel."""

    bpy.utils.register_class(ComfyBlenderPanelWorkflow3DViewer)
    bpy.utils.register_class(ComfyBlenderPanelWorkflowImageEditor)

def unregister():
    """Unregister the panel."""

    bpy.utils.unregister_class(ComfyBlenderPanelWorkflow3DViewer)
    bpy.utils.unregister_class(ComfyBlenderPanelWorkflowImageEditor)

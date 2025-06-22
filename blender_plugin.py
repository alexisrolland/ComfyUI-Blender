import bpy
import json
import os
import requests
import shutil
import subprocess
import sys
import uuid


bl_info = {
    "name": "ComfyUI Blender Plugin",
    "author": "Alexis ROLLAND",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "location": "View3D > Sidebar > ComfyUI",
    "description": "Blender plugin to send requests to a ComfyUI server.",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

# Create the workflows directory if it doesn't exist
WORKFLOW_DIR = os.path.join(os.path.dirname(__file__), "workflows")
os.makedirs(WORKFLOW_DIR, exist_ok=True)



#################
#     Utils     #
#################

def install_dependencies():
    """Install required Python dependencies."""
    required_packages = ["websocket-client"]

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def get_workflow_list(self, context):
    """Return a list of workflows JSON files."""
    workflows = []
    for file in sorted(os.listdir(WORKFLOW_DIR)):
        if file.endswith(".json"):
            workflows.append((file, file, ""))
    return workflows

def parse_workflow_for_inputs(workflow_path):
    """Parse the workflow JSON file and extract nodes with 'class_type' starting with 'BlenderInput...'."""
    inputs = {}
    try:
        with open(workflow_path, "r") as f:
            workflow_data = json.load(f)
            for key, node in workflow_data.items():
                if node.get("class_type").startswith("BlenderInput"):
                    inputs[key]=node
    except Exception as e:
        print(f"Failed to parse workflow: {e}")
    return inputs



####################
#     Settings     #
####################

class ComfyUIAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    server_address: bpy.props.StringProperty(
        name="Server Address",
        description="URL of the ComfyUI server",
        default="http://127.0.0.1:8188"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "server_address", text="Server Address")



#####################
#     Operators     #
#####################

class COMFY_OT_ImportWorkflow(bpy.types.Operator):
    """Operator to import a workflow JSON file."""
    bl_idname = "comfy.import_workflow"
    bl_label = "Import Workflow"
    bl_description = "Import a workflow JSON file"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath.endswith(".json"):
            base_name = os.path.basename(self.filepath)
            destination = os.path.join(WORKFLOW_DIR, base_name)

            # Handle file name conflicts by appending an incremental number
            if os.path.exists(destination):
                name, ext = os.path.splitext(base_name)
                counter = 1
                while os.path.exists(os.path.join(WORKFLOW_DIR, f"{name}_{counter}{ext}")):
                    counter += 1
                destination = os.path.join(WORKFLOW_DIR, f"{name}_{counter}{ext}")

            # Copy the file to the workflows directory
            try:
                shutil.copy(self.filepath, destination)  # Copy the file to the resolved destination
                self.report({'INFO'}, f"Workflow copied to: {destination}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to copy workflow: {e}")
        else:
            self.report({'ERROR'}, "Selected file is not a JSON file.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class COMFY_OT_RunWorkflow(bpy.types.Operator):
    """Operator to update the workflow JSON file and send it to the ComfyUI server."""
    bl_idname = "comfy.run_workflow"
    bl_label = "Run Workflow"
    bl_description = "Send the workflow to the ComfyUI server"

    def execute(self, context):
        # Get the selected workflow
        selected_workflow = context.scene.workflow
        if not selected_workflow:
            self.report({'ERROR'}, "No workflow selected.")
            return {'CANCELLED'}

        workflow_path = os.path.join(WORKFLOW_DIR, selected_workflow)
        workflow_name = os.path.basename(workflow_path)

        # Load the workflow JSON file
        try:
            with open(workflow_path, "r") as f:
                workflow_data = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load workflow: {e}")
            return {'CANCELLED'}

        # Update the workflow with panel values
        for key in workflow_data.keys():
            input = f"wkf_{workflow_name}_{key}"
            if input in context.scene.keys():
                workflow_data[key]["inputs"]["value"] = context.scene[input]

        # Get the server URL from addon preferences
        addon_prefs = context.preferences.addons[__name__].preferences
        server_address = addon_prefs.server_address
        client_id = context.scene.client_id

        # Send the workflow to the ComfyUI server
        try:
            payload = { "prompt": workflow_data, "client_id": client_id }
            response = requests.post(server_address + "/prompt", json=payload)
            if response.status_code == 200:
                self.report({'INFO'}, "Workflow sent successfully.")
                context.scene.prompt_id = response.json().get("prompt_id", "")
            else:
                self.report({'ERROR'}, f"Failed to send workflow: {response.status_code} - {response.text}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to send workflow: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}



#################
#     Panel     #
#################

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

        # Parse the selected workflow and add text inputs
        selected_workflow = context.scene.workflow
        if selected_workflow:
            box = layout.box()
            workflow_path = os.path.join(WORKFLOW_DIR, selected_workflow)
            workflow_name = os.path.basename(workflow_path)
            inputs = parse_workflow_for_inputs(workflow_path)

            # Create properties for each input
            for key, node in inputs.items():
                name = node["_meta"]["title"]
                box.prop(context.scene, f"wkf_{workflow_name}_{key}", text=name)
        
        # Button to run the selected workflow
        box.operator("comfy.run_workflow", text="Run Workflow")

class COMFY_PT_OutputPanel(bpy.types.Panel):
    bl_label = "Outputs"
    bl_idname = "COMFY_PT_OutputPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI"

    def draw(self, context):
        # Get the server address from addon preferences
        addon_prefs = context.preferences.addons[__name__].preferences
        server_address = addon_prefs.server_address.replace("http://", "").replace("https://", "")
        client_id = context.scene.client_id

        # Establish websocket connection to the ComfyUI server
        import websocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

        # Listen for messages from the server
        prompt_id = context.scene.prompt_id
        #while True:
        #    out = ws.recv()
        #    print(out)
        #    if isinstance(out, str):
        #        message = json.loads(out)
        #        if message['type'] == 'executing':
        #            data = message['data']
        #            if data['node'] is None and data['prompt_id'] == prompt_id:
        #                break #Execution is done
        #    else:
                # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
                # bytesIO = BytesIO(out[8:])
                # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
        #        continue #previews are binary data

        layout = self.layout



def register():
    # Install dependencies
    install_dependencies()

    # Properties
    bpy.types.Scene.client_id = bpy.props.StringProperty(
        name="Client Id",
        description="Unique identifier for the client",
        default=str(uuid.uuid4())
    )
    bpy.types.Scene.workflow = bpy.props.EnumProperty(
        name="Workflows",
        description="List of workflows to send to the ComfyUI server",
        items=get_workflow_list
    )
    bpy.types.Scene.prompt_id = bpy.props.StringProperty(
        name="Prompt Id",
        description="Unique identifier of the last prompt sent to the ComfyUI server",
        default=""
    )

    # Dynamically create properties for workflows inputs
    for workflow_file in os.listdir(WORKFLOW_DIR):
        workflow_path = os.path.join(WORKFLOW_DIR, workflow_file)
        workflow_name = os.path.basename(workflow_path)
        inputs = parse_workflow_for_inputs(workflow_path)
        
        # Create properties for each input
        for key, node in inputs.items():
            name = node["_meta"]["title"]
            if node["class_type"] == "BlenderInputFloat":
                setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.FloatProperty(name=name))

            if node["class_type"] == "BlenderInputInt":
                setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.IntProperty(name=name))
            
            if node["class_type"] == "BlenderInputString":
                setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.StringProperty(name=name))

            elif node["class_type"] == "BlenderInputStringMultiline":
                setattr(bpy.types.Scene, f"wkf_{workflow_name}_{key}", bpy.props.StringProperty(name=name))

    # Settings
    bpy.utils.register_class(ComfyUIAddonPreferences)

    # Operators
    bpy.utils.register_class(COMFY_OT_ImportWorkflow)
    bpy.utils.register_class(COMFY_OT_RunWorkflow)

    # Panels
    bpy.utils.register_class(COMFY_PT_InputPanel)
    bpy.utils.register_class(COMFY_PT_OutputPanel)

def unregister():
    # Remove dynamically created properties
    for workflow_file in os.listdir(WORKFLOW_DIR):
        workflow_path = os.path.join(WORKFLOW_DIR, workflow_file)
        inputs = parse_workflow_for_inputs(workflow_path)
        for key in inputs.keys():
            delattr(bpy.types.Scene, f"comfy_input_{key}")

    # Panels
    bpy.utils.unregister_class(COMFY_PT_InputPanel)
    bpy.utils.unregister_class(COMFY_PT_OutputPanel)

    # Operators
    bpy.utils.unregister_class(COMFY_OT_ImportWorkflow)
    bpy.utils.unregister_class(COMFY_OT_RunWorkflow)

    # Settings
    bpy.utils.unregister_class(ComfyUIAddonPreferences)

    # Properties
    del bpy.types.Scene.client_id
    del bpy.types.Scene.workflow

if __name__ == "__main__":
    register()
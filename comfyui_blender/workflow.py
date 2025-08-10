"""Functions to create dynamic workflow classes and properties"""
import json
import os
import re

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty
)


def create_class_properties(inputs, keep_values=False):
    """Create properties for each input and output of the workflow."""

    properties = {}
    for key, node in inputs.items():
        property_name = f"node_{key}"
        property_name = re.sub(r"[^a-zA-Z0-9_]", "_", property_name).lower()        
        metadata = node.get("_meta", {})
        name = metadata.get("title", f"Node {key}")

        # Input properties
        # Boolean
        if node["class_type"] == "BlenderInputBoolean":
            properties[property_name] = BoolProperty(
                name=name,
                default=node["inputs"].get("default", False)
            )
            continue

        # Combo box
        if node["class_type"] == "BlenderInputCombo":
            # If default value not in list, set to first item in the list
            default = node["inputs"].get("default", "")
            items = node["inputs"]["list"].split("\n")
            if default not in items:
                default = items[0]

            properties[property_name] = EnumProperty(
                name=name,
                default=default,
                items=[(i, i, "") for i in items]
            )
            continue

        # Float
        if node["class_type"] == "BlenderInputFloat":
            properties[property_name] = FloatProperty(
                name=name,
                default=node["inputs"].get("default", 0.0),
                min=node["inputs"].get("min", -1e38),
                max=node["inputs"].get("max", 1e38),
                # Step size is weird, value of 1 gives a step of 0.1, so I'm deactivating it for now
                # step=node["inputs"].get("step", 1.0),
                step=1,
                precision=2
            )
            continue

        # Integer
        if node["class_type"] == "BlenderInputInt":
            properties[property_name] = IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", -2147483648),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            )
            continue

        # Load 3D and Load image
        if node["class_type"] in ("BlenderInputLoad3D", "BlenderInputLoadImage"):
            properties[property_name] = StringProperty(name=name)
            continue
        
        # Seed
        if node["class_type"] == "BlenderInputSeed":
            properties[property_name] = IntProperty(
                name=name,
                default=node["inputs"].get("default", 0),
                min=node["inputs"].get("min", 0),
                max=node["inputs"].get("max", 2147483647),
                step=node["inputs"].get("step", 1)
            )
            continue

        # String and String multiline
        if node["class_type"] in ("BlenderInputString", "BlenderInputStringMultiline"):
            properties[property_name] = StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            )
            continue
    return properties

def create_workflow_class(class_name, properties):
    """Create a new PropertyGroup class for a workflow."""

    # Create the new class
    new_class = type(class_name, (bpy.types.PropertyGroup,), {})

    # Add properties to the class
    for prop_name, prop_details in properties.items():
        setattr(new_class, prop_name, prop_details)

    # Manually add the annotations attribute
    new_class.__annotations__ = {prop_name: properties[prop_name] for prop_name in properties}
    return new_class

def get_workflow_class_name(workflow_filename):
    """Generate a class name from the workflow file name."""

    workflow_name = os.path.splitext(workflow_filename)[0]
    class_name = f"wkf_{workflow_name}"
    class_name = re.sub(r"[^a-zA-Z0-9_]", "_", class_name).lower()
    return class_name

def get_workflow_list(self, context):
    """Return a list of workflow JSON files from the workflows folder."""

    addon_prefs = context.preferences.addons["comfyui_blender"].preferences
    workflows_folder = addon_prefs.workflows_folder
    workflows = []

    if os.path.exists(workflows_folder) and os.path.isdir(workflows_folder):
        for file in sorted(os.listdir(workflows_folder)):
            if file.endswith(".json"):
                filepath = os.path.join(workflows_folder, file)
                workflows.append((file, file, filepath))

    # Default to empty tuple if there are no workflow
    if not workflows:
        workflows = [("none", "None", "No workflow available")]
    return workflows

def parse_workflow_for_inputs(workflow):
    """Parse a workflow dictionary and extract nodes with 'class_type' starting with 'BlenderInput...'."""

    inputs = {}
    sorted_inputs = inputs
    for key, node in workflow.items():
        class_type = node.get("class_type")
        if class_type:
            if class_type.startswith("BlenderInput"):
                inputs[key]=node

    if len(inputs) > 0:
        # Reorder the keys based on the "order" property of the nodes dictionaries
        sorted_keys = sorted(inputs.keys(), key=lambda k: inputs[k]["inputs"]["order"])

        # Create a new dictionary with the sorted keys
        sorted_inputs = {key: inputs[key] for key in sorted_keys}
    return sorted_inputs

def parse_workflow_for_outputs(workflow):
    """Parse a workflow dictionary and extract nodes with 'class_type' starting with 'BlenderOutput...'."""

    outputs = {}
    for key, node in workflow.items():
        class_type = node.get("class_type")
        if class_type:
            if class_type.startswith("BlenderOutput"):
                outputs[key]=node
    return outputs

def register_workflow_class(self, context):
    """Wrapper function to register a workflow class."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    workflows_folder = str(addon_prefs.workflows_folder)
    workflow_filename = str(self.workflow)
    workflow_path = os.path.join(workflows_folder, workflow_filename)
    workflow_class_name = get_workflow_class_name(workflow_filename)

    # Unregister workflow class if it already exists
    for subclass in bpy.types.PropertyGroup.__subclasses__():
        if subclass.__name__==workflow_class_name and subclass.is_registered:
            bpy.utils.unregister_class(subclass)

    # Load the workflow JSON file
    if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
        with open(workflow_path, "r",  encoding="utf-8") as file:
            workflow = json.load(file)

        # Get inputs from the workflow
        inputs = parse_workflow_for_inputs(workflow)
        properties = create_class_properties(inputs)
        workflow_class = create_workflow_class(workflow_class_name, properties)

        # Register the workflow class
        bpy.utils.register_class(workflow_class)
        bpy.types.Scene.current_workflow = bpy.props.PointerProperty(type=workflow_class)

        # Get custom data from the workflow
        keep_values = False
        if workflow.get("comfyui_blender"):
            keep_values = workflow["comfyui_blender"].get("keep_values", False)

        # Overwrite values after registration
        # Note keep_values is set to True when reloading a workflow from outputs
        if hasattr(context.scene, "current_workflow") and keep_values:
            workflow_instance = context.scene.current_workflow
            for key, node in inputs.items():
                property_name = f"node_{key}"
                property_name = re.sub(r"[^a-zA-Z0-9_]", "_", property_name).lower()
                if hasattr(workflow_instance, property_name):
                    setattr(workflow_instance, property_name, node["inputs"].get("value", ""))

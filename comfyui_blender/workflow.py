"""Functions to create dynamic workflow classes and properties"""
import json
import os
import re

import bpy
from bpy.props import (
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty
)


def create_class_properties(dictionary):
    """Create dynamic properties for each input and output of the workflow."""

    properties = {}
    for key, node in dictionary.items():
        property_name = f"node_{key}"
        property_name = re.sub(r"[^a-zA-Z0-9_]", "_", property_name).lower()        
        metadata = node.get("_meta", {})
        name = metadata.get("title", f"Node {key}")

        # Input properties
        # Combo box
        if node["class_type"] == "BlenderInputCombo":
            properties[property_name] = EnumProperty(
                name=name,
                default=node["inputs"].get("default", ""),
                items=[(i, i, "") for i in node["inputs"]["list"].split("\n")]
            )
            continue

        # Float
        if node["class_type"] == "BlenderInputFloat":
            properties[property_name] = FloatProperty(
                name=name,
                default=node["inputs"].get("default", 0.0),
                min=node["inputs"].get("min", -1e38),
                max=node["inputs"].get("max", 1e38),
                step=node["inputs"].get("step", 0.01)
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

        # String
        if node["class_type"] == "BlenderInputString":
            properties[property_name] = StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            )
            continue

        # String multiline
        elif node["class_type"] == "BlenderInputStringMultiline":
            properties[property_name] = StringProperty(
                name=name,
                default=node["inputs"].get("default", "")
            )
            continue
        
        # Output properties
        # Save image
        if node["class_type"] == "BlenderOutputSaveImage":
            properties[property_name] = StringProperty(name=name)
    return properties

def create_workflow_class(workflow_file, inputs_properties):
    """Create a new PropertyGroup class for a workflow."""

    # Generate a class name from the workflow file name
    workflow_name = os.path.splitext(workflow_file)[0]
    class_name = f"wkf_{workflow_name}"
    class_name = re.sub(r"[^a-zA-Z0-9_]", "_", class_name).lower()

    # Create the new class
    new_class = type(class_name, (bpy.types.PropertyGroup,), {})

    # Add properties to the class
    for prop_name, prop_details in inputs_properties.items():
        setattr(new_class, prop_name, prop_details)

    # Manually add the annotations attribute
    new_class.__annotations__ = {prop_name: inputs_properties[prop_name] for prop_name in inputs_properties}

    return new_class

def get_workflow_list(self, context):
    """Return a list of workflows JSON files from the workflows folder."""

    addon_prefs = context.preferences.addons["comfyui_blender"].preferences
    workflows_folder = addon_prefs.workflows_folder
    workflows = []

    if os.path.exists(workflows_folder) and os.path.isdir(workflows_folder):
        for file in sorted(os.listdir(workflows_folder)):
            if file.endswith(".json"):
                workflows.append((file, file, ""))

    # Default to empty tuple if there are no workflow
    if not workflows:
        workflows = [("none", "None", "No workflow available")]
    return workflows

def parse_workflow_for_inputs(workflow):
    """Parse a workflow dictionary and extract nodes with 'class_type' starting with 'BlenderInput...'."""

    inputs = {}
    sorted_inputs = inputs
    for key, node in workflow.items():
        if node.get("class_type").startswith("BlenderInput"):
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
        if node.get("class_type").startswith("BlenderOutput"):
            outputs[key]=node
    return outputs

def register_workflow_class(self, context):
    """Wrapper function to register a workflow class."""

    addon_prefs = bpy.context.preferences.addons["comfyui_blender"].preferences
    workflows_folder = str(addon_prefs.workflows_folder)
    workflow_file = str(self.workflow)
    workflow_path = os.path.join(workflows_folder, workflow_file)

    # Load the workflow JSON file
    if os.path.exists(workflow_path) and os.path.isfile(workflow_path):
        with open(workflow_path, "r",  encoding="utf-8") as f:
            workflow = json.load(f)

        # Get inputs and outputs from the workflow
        inputs = parse_workflow_for_inputs(workflow)
        outputs = parse_workflow_for_outputs(workflow)
        properties = create_class_properties({**inputs, **outputs}) # Merge dictionaries
        workflow_class = create_workflow_class(workflow_file, properties)

        # Unregister the class if it already exists
        if hasattr(bpy.types, workflow_class.__name__):
            unregister(workflow_class)
        register(workflow_class)

def register(workflow_class):
    """Register the panel."""

    bpy.utils.register_class(workflow_class)
    bpy.types.Scene.current_workflow = bpy.props.PointerProperty(type=workflow_class)

def unregister(workflow_class):
    """Unregister the panel."""

    bpy.utils.unregister_class(workflow_class)
    del bpy.types.Scene.current_workflow

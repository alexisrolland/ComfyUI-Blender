"""Operator to get a random seed value."""
import bpy
import random


class ComfyBlenderOperatorGetRandomSeed(bpy.types.Operator):
    """Operator to get a random seed value."""

    bl_idname = "comfy.get_random_seed"
    bl_label = "Get Random Seed"
    bl_description = "Get a random seed value."

    workflow_property: bpy.props.StringProperty(name="Workflow Property")

    def execute(self, context):
        """Execute the operator."""
        
        # Get current workflow property
        current_workflow = context.scene.current_workflow
        
        # Get the property descriptor to access min/max
        prop_descriptor = current_workflow.bl_rna.properties[self.workflow_property]
        
        # For IntProperty or FloatProperty, use soft_min/soft_max or hard_min/hard_max
        min_value = getattr(prop_descriptor, "soft_min", getattr(prop_descriptor, "hard_min", 0))
        max_value = getattr(prop_descriptor, "soft_max", getattr(prop_descriptor, "hard_max", 2147483647))
        random_seed = random.randint(min_value, max_value)

        # Set the workflow property
        setattr(current_workflow, self.workflow_property, random_seed)
        return {'FINISHED'}


def register():
    """Register the operator."""

    bpy.utils.register_class(ComfyBlenderOperatorGetRandomSeed)


def unregister():
    """Unregister the operator."""

    bpy.utils.unregister_class(ComfyBlenderOperatorGetRandomSeed)

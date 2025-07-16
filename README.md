# ComfyUI Blender

> Alpha version: This is functional but WORK IN PROGRESS, with a few quirks to be improved over time

Blender add-on to send requests to a ComfyUI server. This respository contains both custom nodes to be installed on the ComfyUI server and the source code of the Blender add-on.

## Getting Started

### Install ComfyUI Custom Nodes

Install the custom nodes on your ComfyUI server:

```shell
cd ./ComfyUI/custom_nodes
git clone https://github.com/alexisrolland/ComfyUI-Blender.git
```

Note these nodes do not require any Python dependency. They are only used to define the inputs and outputs of the workflows to be displayed in the Blender add-on.

### Install Blender Add-on

Download the add-on package `comfyui_blender_[...].zip` from the **[LATEST RELEASE](https://github.com/alexisrolland/ComfyUI-Blender/releases)**.

In Blender, go to `Edit` > `Preferences` > `Add-ons` > `Install from Disk` > select the zip package.

## Usage

1. Create a workflow in ComfyUI (you can refer to the workflow examples in this repository). Make sure to use the ComfyUI Blender nodes to define the inputs and outputs of your workflow you wish to display in the Blender add-on.

2. Export the workflow **in API format**: `Workflow` > `Export (API)`.

3. In the Blender add-on import the workflow JSON file from the ComfyUI Workflow panel.

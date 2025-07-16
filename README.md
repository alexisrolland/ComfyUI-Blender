# ComfyUI Blender

> Alpha version: This is functional but WORK IN PROGRESS, with a few quirks to be improved over time

Blender add-on to send requests to a ComfyUI server. This respository contains both custom nodes to be installed on the ComfyUI server and the source code of the Blender add-on.

![Blender Screenshot](./screenshot_blender.jpg)

## Getting Started

### Install ComfyUI Custom Nodes

Install the custom nodes on your ComfyUI server. They can be installed from the ComfyUI Manager or by cloning this repository:

```shell
cd ./ComfyUI/custom_nodes
git clone https://github.com/alexisrolland/ComfyUI-Blender.git
```

Note these nodes do not require additional Python dependencies. They are only used to define the inputs and outputs of the workflows to be displayed in the Blender add-on.

### Install Blender Add-on

Download the add-on package `comfyui_blender_[...].zip` from the **[LATEST RELEASE](https://github.com/alexisrolland/ComfyUI-Blender/releases)**.

In Blender, go to `Edit` > `Preferences` > `Add-ons` > `Install from Disk` > select the zip package.

## Usage

1. Create a workflow in ComfyUI (see workflow examples in this repository).

2. Use the Blender nodes to define the inputs and outputs of the workflow to be displayed in the Blender add-on.

3. Export the workflow **in API format**: `Workflow` > `Export (API)`.

4. In the Blender add-on import the workflow JSON file from the ComfyUI Workflow panel.

5. Update the inputs and click on **Run Workflow**.

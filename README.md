# ComfyUI Blender

[![ComfyUI Registry](https://img.shields.io/badge/comfyui-registry-grey?labelColor=blue)](https://registry.comfy.org/nodes/comfyui-blender)
[![Latest Release](https://img.shields.io/github/v/release/alexisrolland/ComfyUI-Blender)](https://github.com/alexisrolland/ComfyUI-Blender/releases/latest)

This is a Blender add-on to send requests to a ComfyUI server. This respository contains both custom nodes to be installed on the ComfyUI server and the source code of the Blender add-on.

## How Is It Different ?

This Blender add-on allows to use any ComfyUI workflow and dynamically displays input controls with a simple UI in the add-on panel:

* Create a workflow in ComfyUI **with the Blender nodes**.
* Export the workflow **in API format**.
* Import the workflow in the Blender add-on... voilà!

Both the custom nodes and add-on are lightweight and simple to install, with no extra dependencies beside the `websocket-client` required by the add-on to retrieve results from the ComfyUI server.

![Screenshot Blender](./screenshot_blender.jpg)

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

1. In ComfyUI, create a workflow using the Blender nodes (see workflow examples in this repository).

    * The Blender nodes are used to define the inputs and outputs to be displayed in the Blender add-on.
    * The title of the nodes are used as labels in the Blender add-on panel.

![Screenshot ComfyUI](./screenshot_comfyui.png)

2. Export the workflow JSON file **in API format**: `Workflow` > `Export (API)`.

3. In Blender, import the workflow JSON file (make sure it is in API format): Press `N` > `ComfyUI` > `Import Workflow`.

4. Update the inputs and click on **Run Workflow**.

## Features

Below is a non exhaustive list of features that require some explanations.

### Blender Input Combo

The node `Blender Input Combo` provides the following settings in ComfyUI:

* **list**: A list of values that will be displayed in a dropdown box in Blender (one item per line).
* **format_path**: If `True` and if the value provided to the node is a path, it will be formatted according the operating system ComfyUI runs on. This is particularly useful for lists of models that are contained in subfolders.

### Blender Input Load 3D

The node `Blender Input Load 3D` provides the following features in Blender:

* **Prepare 3D Model**: Prepare an `.obj` file with the selected meshes to be sent to the ComfyUI server.

### Blender Input Load Image

The node `Blender Input Load Image` provides the following features in Blender:

* **Import Image**: Import a custom image.
* **Render View**: Render an image from the camera.
* **Render Depth Map**: Render a depth map from the camera.
* **Render Lineart**: Render a lineart from the camera.

### Blender Input String & Blender Input String Multiline

The nodes `Blender Input String` & `Blender Input String Multiline` provide the following settings in ComfyUI:

* **format_path**: If `True` and if the value provided to the node is a path, it will be formatted according the operating system ComfyUI runs on. This is particularly useful for input file paths that are contained in subfolders.

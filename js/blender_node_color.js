import { app } from "../../scripts/app.js";

function setNodeColor(node) {
  if (node.comfyClass?.startsWith("BlenderInput") || node.comfyClass?.startsWith("BlenderOutput")) {
    if (!node.color) node.color = "#432";
    if (!node.bgcolor) node.bgcolor = "#653";
    node.setDirtyCanvas(true, true);
  }
}

app.registerExtension({
  name: "comfyui_blender.node_color",
  async nodeCreated(node) {
    setNodeColor(node);
  },
  async loadedGraphNode(node) {
    setNodeColor(node);
  },
});
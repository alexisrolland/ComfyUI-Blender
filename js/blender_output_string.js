import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "comfyui_blender.BlenderOutputString",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "BlenderOutputString") {

            // Add a text widget on node creation
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated ? onNodeCreated.apply(this, []) : undefined
                const showValueWidget = ComfyWidgets["STRING"](this, "output", ["STRING", { multiline: true }], app).widget;
                showValueWidget.inputEl.readOnly = true;
                showValueWidget.serialize = false;
            };

            // Update content on node execution
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted === null || onExecuted === void 0
                ? void 0
                : onExecuted.apply(this, [message])

                const previewWidget = this.widgets?.find((w) => w.name === "output")
                if (previewWidget) {
                    previewWidget.value = message.text[0]
                }
            };
        }
    }
});
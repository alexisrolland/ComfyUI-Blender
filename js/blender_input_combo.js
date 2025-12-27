import { api } from "../../scripts/api.js"
import { app } from "../../scripts/app.js"

// Frontend extension for the node BlenderInputCombo
// Retrieves the list of possible values from the connected output socket and displays them in the "list" widget
app.registerExtension({
    name: "comfyui_blender.BlenderInputCombo",
    async nodeCreated(node) {
        if (node.comfyClass === "BlenderInputCombo") {
            node.onConnectionsChange = async function (_, changedOutputId, isConnected, linkInfo) {
                // Do nothing if the changed output is not the "COMBO" output socket or if it is disconnected
                const comboSlot = node.outputs.findIndex(o => o.name === "COMBO")
                if (changedOutputId !== comboSlot) { return }
                if (!isConnected) { return }
                if (!linkInfo) { return }

                // Get the target node to retrieve possible values from
                const targetNode = app.graph.getNodeById(linkInfo.target_id)
                const targetInputSlot = targetNode.inputs[linkInfo.target_slot]
                const targetInputName = targetInputSlot.name
                const targetClassName = targetNode.comfyClass

                // Fetch values and update the list widget
                try {
                    const info = await api.fetchApi(`/object_info/${targetClassName}`)
                    const json = await info.json()
                    const target = json[targetClassName].input.required[targetInputName]

                    // Get values from the target input
                    let values = []
                    if (Array.isArray(target[0])) { values = target[0] }  // Handles cases where the target is a list of values (sampler, scheduler...)
                    else if (target[0] == "COMBO") { values = target[1].options } // Handles cases where the target is a custom COMBO
                    else { values = [target[0]] }

                    // Assign values only if the list widget is empty
                    const listWidget = node.widgets.find(w => w.name === "list")
                    listWidget.value = !listWidget.value ? values.join("\n") : listWidget.value
                }
                catch (e) {
                    console.error("BlenderInputCombo: " + e)
                }
            }
        }
    }
})

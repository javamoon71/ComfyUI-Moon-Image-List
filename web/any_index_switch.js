// Any Index Switch 노드의 value 입력 슬롯을 연결 상태에 맞춰 자동으로 늘리고 줄이는 프론트엔드 확장
import { app } from "../../scripts/app.js";

const VALUE_NAME = /^value\d+$/;

// 마지막 value 슬롯이 연결되면 다음 슬롯을 추가하고, 끝에 연속으로 비어 있는 슬롯은 하나만 남긴다.
// 중간의 빈 슬롯은 지우지 않는다. 슬롯 이름이 value0부터 빈틈없이 이어지도록 끝에서만 늘리고 줄인다
function syncValueInputs(node) {
  const values = node.inputs.filter((input) => VALUE_NAME.test(input.name));
  let changed = false;
  while (values.length > 1 && values.at(-1).link == null && values.at(-2).link == null) {
    node.removeInput(node.inputs.indexOf(values.pop()));
    changed = true;
  }
  if (!values.length || values.at(-1).link != null) {
    node.addInput(`value${values.length}`, "*");
    changed = true;
  }
  if (changed) node.setSize([node.size[0], node.computeSize()[1]]);
}

app.registerExtension({
  name: "ComfyUI-Moon-Tools.AnyIndexSwitch",
  beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "AnyIndexSwitch") return;
    const onConnectionsChange = nodeType.prototype.onConnectionsChange;
    nodeType.prototype.onConnectionsChange = function (...args) {
      onConnectionsChange?.apply(this, args);
      // 링크를 다른 슬롯으로 옮기면 끊기와 연결이 이어서 일어나므로, 둘 다 끝난 뒤에 슬롯을 맞춘다
      queueMicrotask(() => syncValueInputs(this));
    };
  },
});

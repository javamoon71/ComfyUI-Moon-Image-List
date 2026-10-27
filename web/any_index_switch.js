// Any Index Switch 노드의 value 입력 슬롯을 연결 상태에 맞춰 자동으로 늘리고 줄이고, 생성 후 제어가 index를 순환시키게 하는 프론트엔드 확장
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

// 생성 후 제어가 index를 연결된 입력 범위(0 ~ 개수-1) 안에서 순환시키게 한다.
// 기본 제어는 min/max에서 멈추고 randomize는 max를 뽑지 않으므로, 제어가 도는 동안만 범위를 넓힌 뒤 넘친 값을 반대쪽 끝으로 돌린다.
// index 입력이 링크로 연결되어 있으면 기본 제어가 값을 바꾸지 않는다
function wrapIndexControl(node) {
  const index = node.widgets?.find((widget) => widget.name === "index");
  const control = index?.linkedWidgets?.[0];
  if (!control) return;
  for (const hook of ["beforeQueued", "afterQueued"]) {
    const original = control[hook];
    control[hook] = function (...args) {
      const count = node.inputs.filter((input) => VALUE_NAME.test(input.name) && input.link != null).length;
      if (!count || control.value === "fixed") return original?.apply(this, args);
      const { min, max } = index.options;
      index.value %= count;
      index.options.min = control.value === "randomize" ? 0 : -1;
      index.options.max = count;
      try {
        original?.apply(this, args);
      } finally {
        index.options.min = min;
        index.options.max = max;
      }
      const wrapped = index.value >= count ? 0 : index.value < 0 ? count - 1 : index.value;
      if (wrapped !== index.value) {
        index.value = wrapped;
        index.callback?.(wrapped);
      }
    };
  }
}

app.registerExtension({
  name: "ComfyUI-Moon-Tools.AnyIndexSwitch",
  beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "AnyIndexSwitch") return;
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function (...args) {
      onNodeCreated?.apply(this, args);
      wrapIndexControl(this);
    };
    const onConnectionsChange = nodeType.prototype.onConnectionsChange;
    nodeType.prototype.onConnectionsChange = function (...args) {
      onConnectionsChange?.apply(this, args);
      // 링크를 다른 슬롯으로 옮기면 끊기와 연결이 이어서 일어나므로, 둘 다 끝난 뒤에 슬롯을 맞춘다
      queueMicrotask(() => syncValueInputs(this));
    };
  },
});

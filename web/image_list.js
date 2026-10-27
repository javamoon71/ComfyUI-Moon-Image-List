// Image List 노드의 IMAGE_LIST 입력을 썸네일 목록으로 보여주고, 이미지 업로드/삭제로 항목을 관리하는 프론트엔드 확장
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const THUMB_SIZE = 128;
const ADD_BUTTON_HEIGHT = 30;
const GAP = 4;

function parseValue(value) {
  try {
    const parsed = JSON.parse(String(value ?? ""));
    if (Array.isArray(parsed)) return parsed.map(String).filter((v) => v.trim());
  } catch {}
  return String(value ?? "").split("\n").filter((v) => v.trim());
}

// 저장 이름은 기본 Load Image와 같은 "subfolder/name" 형식이다
function thumbnailUrl(item) {
  const slash = item.lastIndexOf("/");
  const subfolder = slash < 0 ? "" : item.slice(0, slash);
  const filename = item.slice(slash + 1);
  const params = new URLSearchParams({ filename, subfolder, type: "input" });
  return api.apiURL(`/view?${params}`);
}

async function uploadImage(file) {
  const body = new FormData();
  body.append("image", file);
  const resp = await api.fetchApi("/upload/image", { method: "POST", body });
  if (resp.status !== 200) throw new Error(`${resp.status} ${resp.statusText}`);
  const data = await resp.json();
  return data.subfolder ? `${data.subfolder}/${data.name}` : data.name;
}

function createImageListWidget(node, inputName) {
  let items = [];

  // 노드 높이는 사용자가 정한 대로 두고, 넘치는 항목은 list 안에서 스크롤한다. 추가 버튼은 list 아래에 고정한다
  const container = document.createElement("div");
  container.style.cssText = `display:flex;flex-direction:column;gap:${GAP}px;padding:4px 0;height:100%;box-sizing:border-box;`;
  const list = document.createElement("div");
  list.style.cssText = `flex:1;min-height:0;overflow-y:auto;display:flex;flex-direction:column;gap:${GAP}px;`;
  container.append(list);

  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/*";
  fileInput.multiple = true;
  fileInput.style.display = "none";
  container.append(fileInput);

  // index 위젯의 최대값을 항목 수에 맞춰 화살표로 범위를 넘지 않게 한다
  const refreshIndexRange = () => {
    const indexWidget = node.widgets?.find((w) => w.name === "index");
    if (!indexWidget) return;
    const max = Math.max(0, items.length - 1);
    indexWidget.options.max = max;
    if (indexWidget.value > max) indexWidget.value = max;
  };

  const createButton = (text, title, onClick) => {
    const button = document.createElement("button");
    button.textContent = text;
    button.title = title;
    button.addEventListener("click", onClick);
    return button;
  };

  const render = () => {
    list.replaceChildren();
    if (items.length === 0) {
      const empty = document.createElement("div");
      empty.textContent = "(이미지 없음)";
      empty.style.cssText = "opacity:0.5;font-size:12px;padding:4px 6px;";
      list.append(empty);
    }
    items.forEach((item, i) => {
      const row = document.createElement("div");
      row.style.cssText =
        `display:flex;align-items:center;gap:${GAP}px;flex-shrink:0;padding:2px;border-radius:4px;` +
        "border:1px solid var(--border-color);background:var(--comfy-input-bg);color:var(--input-text);";

      const label = document.createElement("span");
      label.textContent = String(i);
      label.style.cssText = "min-width:24px;text-align:right;opacity:0.7;font-size:12px;";

      const thumb = document.createElement("img");
      thumb.src = thumbnailUrl(item);
      thumb.title = item;
      thumb.style.cssText = `width:${THUMB_SIZE}px;height:${THUMB_SIZE}px;object-fit:contain;flex-shrink:0;background:#0003;`;

      const name = document.createElement("span");
      name.textContent = item;
      name.title = item;
      name.style.cssText = "flex:1;min-width:0;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;";

      const remove = createButton("✕", "항목 삭제", () => {
        items.splice(i, 1);
        render();
      });
      remove.style.cssText = "width:24px;height:24px;flex-shrink:0;cursor:pointer;";

      row.append(label, thumb, name, remove);
      list.append(row);
    });
    refreshIndexRange();
  };

  const add = createButton("+ 이미지 추가", "이미지 업로드", () => fileInput.click());
  add.style.cssText = `height:${ADD_BUTTON_HEIGHT - 4}px;flex-shrink:0;cursor:pointer;`;
  container.append(add);

  const addFiles = async (files) => {
    add.disabled = true;
    try {
      for (const file of files) {
        if (!file.type.startsWith("image/")) continue;
        try {
          items.push(await uploadImage(file));
        } catch (e) {
          alert(`이미지 업로드 실패: ${file.name}\n${e.message}`);
        }
        render();
      }
    } finally {
      add.disabled = false;
    }
  };

  fileInput.addEventListener("change", () => {
    const files = [...fileInput.files];
    fileInput.value = "";
    addFiles(files);
  });

  // 목록 위에 파일을 끌어다 놓으면 업로드한다. ComfyUI가 이미지를 워크플로로 불러오지 않도록 이벤트 전파를 막는다
  const hasFiles = (e) => e.dataTransfer?.types?.includes("Files");
  container.addEventListener("dragover", (e) => {
    if (!hasFiles(e)) return;
    e.preventDefault();
    e.stopPropagation();
    list.style.outline = "2px dashed var(--input-text)";
  });
  container.addEventListener("dragleave", (e) => {
    if (!container.contains(e.relatedTarget)) list.style.outline = "";
  });
  container.addEventListener("drop", (e) => {
    list.style.outline = "";
    if (!hasFiles(e)) return;
    e.preventDefault();
    e.stopPropagation();
    addFiles([...e.dataTransfer.files]);
  });

  const widget = node.addDOMWidget(inputName, "IMAGE_LIST", container, {
    getValue: () => JSON.stringify(items),
    setValue: (value) => {
      items = parseValue(value);
      render();
    },
    // 최소 높이: 항목 하나 + 추가 버튼
    getMinHeight: () => THUMB_SIZE + 6 + GAP + ADD_BUTTON_HEIGHT + 8,
  });

  widget.refreshIndexRange = refreshIndexRange;
  widget.addFiles = addFiles;
  render();
  return { widget };
}

app.registerExtension({
  name: "ComfyUI-Moon-Image-List.ImageList",
  getCustomWidgets() {
    return {
      IMAGE_LIST: (node, inputName) => createImageListWidget(node, inputName),
    };
  },
  // IMAGE_LIST 위젯이 만들어질 때는 index 위젯이 아직 없어서 노드 생성 후 한 번 더 맞춘다
  nodeCreated(node) {
    const widget = node.widgets?.find((w) => w.type === "IMAGE_LIST");
    if (!widget) return;
    widget.refreshIndexRange();
    // 목록 밖(제목, 다른 위젯 영역)에 놓아도 이 노드에 추가한다
    node.onDragOver = (e) => !!e.dataTransfer?.types?.includes("Files");
    node.onDragDrop = (e) => {
      const files = [...(e.dataTransfer?.files ?? [])].filter((f) => f.type.startsWith("image/"));
      if (!files.length) return false;
      widget.addFiles(files);
      return true;
    };
  },
});

// Text List 노드의 TEXT_LIST 입력을 항목 목록으로 보여주고, 클릭한 항목을 여러 줄 입력창으로 편집하게 하는 프론트엔드 확장
import { app } from "../../scripts/app.js";

const LINE_HEIGHT = 18;
const ROW_PADDING = 12;
const ADD_BUTTON_HEIGHT = 30;
const GAP = 4;
const MAX_EDIT_LINES = 10;
const MIN_VIEW_LINES = 2;
const TITLE_HEIGHT = 24;

// 항목은 { title, text }. 제목이 생기기 전 워크플로는 문자열 항목이다
function toItem(value) {
  if (value && typeof value === "object") return { title: String(value.title ?? ""), text: String(value.text ?? "") };
  return { title: "", text: String(value ?? "") };
}

// 예전 워크플로는 줄 단위 문자열로 저장되어 있다
function parseValue(value) {
  const text = String(value ?? "");
  try {
    const parsed = JSON.parse(text);
    if (Array.isArray(parsed)) return parsed.length ? parsed.map(toItem) : [toItem("")];
  } catch {}
  return text.split("\n").map(toItem);
}

function createTextListWidget(node, inputName) {
  let items = [toItem("")];
  let editing = -1;
  let viewLines = MIN_VIEW_LINES;

  // 노드 높이는 사용자가 정한 대로 두고, 넘치는 항목은 list 안에서 스크롤한다. 추가 버튼은 list 아래에 고정한다
  const container = document.createElement("div");
  container.style.cssText = `display:flex;flex-direction:column;gap:${GAP}px;padding:4px 0;height:100%;box-sizing:border-box;`;
  const list = document.createElement("div");
  list.style.cssText = `flex:1;min-height:0;overflow-y:auto;display:flex;flex-direction:column;gap:${GAP}px;`;
  container.append(list);

  // show_title 위젯이 Off면 보기/편집 모드 모두 제목을 숨긴다
  const showTitle = () => node.widgets?.find((w) => w.name === "show_title")?.value !== false;

  // 편집 중인 입력창은 한 줄 여유를 두되 최대 줄 수를 넘으면 입력창 안에서 스크롤한다
  const editLineCount = (i) => Math.min(items[i].text.split("\n").length + 1, MAX_EDIT_LINES);

  // index 위젯의 최대값을 항목 수에 맞춰 화살표로 범위를 넘지 않게 한다
  const refreshIndexRange = () => {
    const indexWidget = node.widgets?.find((w) => w.name === "index");
    if (!indexWidget) return;
    const max = Math.max(0, items.filter((v) => v.text.trim()).length - 1);
    indexWidget.options.max = max;
    if (indexWidget.value > max) indexWidget.value = max;
  };

  // Python이 빈 항목을 건너뛰므로 번호도 비어 있지 않은 항목만 센다
  const refreshLabels = () => {
    let n = 0;
    list.querySelectorAll("span[data-label]").forEach((el, i) => {
      el.textContent = items[i].text.trim() ? String(n++) : "-";
    });
    refreshIndexRange();
  };

  // 제목 label을 눌렀으면 제목 입력창에, 내용을 눌렀으면 내용 입력창에 포커스를 둔다
  const startEdit = (i, field = "text") => {
    editing = i;
    render();
    list.querySelector(field === "title" ? "input" : "textarea")?.focus();
  };

  const createButton = (text, title, onClick) => {
    const button = document.createElement("button");
    button.textContent = text;
    button.title = title;
    // 편집 중인 입력창의 blur로 다시 그려져 클릭이 사라지지 않게 포커스 이동을 막는다
    button.addEventListener("mousedown", (e) => e.preventDefault());
    button.addEventListener("click", onClick);
    return button;
  };

  // 제목(1줄)을 내용 바로 위에 둔다. 보기 모드에서는 둘 다 글자로, 편집 모드에서는 둘 다 입력창으로 보여준다
  const createBody = (item, i) => {
    const body = document.createElement("div");
    body.style.cssText = "flex:1;min-width:0;display:flex;flex-direction:column;gap:2px;";

    const boxStyle =
      "min-width:0;padding:4px 6px;border-radius:4px;font:inherit;font-size:12px;" +
      `line-height:${LINE_HEIGHT}px;white-space:pre-wrap;word-break:break-all;box-sizing:border-box;` +
      "border:1px solid var(--border-color);background:var(--comfy-input-bg);color:var(--input-text);";
    const titleStyle =
      `height:${TITLE_HEIGHT}px;min-width:0;padding:0 6px;border-radius:4px;font:inherit;font-size:12px;font-weight:bold;` +
      `line-height:${TITLE_HEIGHT - 2}px;box-sizing:border-box;color:var(--input-text);`;

    if (i !== editing) {
      const title = document.createElement("div");
      title.textContent = item.title || "(제목 없음)";
      title.style.cssText =
        titleStyle +
        "border:1px solid transparent;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" +
        `cursor:text;${item.title ? "" : "opacity:0.5;font-weight:normal;"}`;
      title.addEventListener("click", () => startEdit(i, "title"));

      const view = document.createElement("div");
      view.textContent = item.text || "(비어 있음)";
      view.dataset.view = "";
      view.style.cssText =
        boxStyle +
        `display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:${viewLines};overflow:hidden;` +
        `cursor:text;${item.text ? "" : "opacity:0.5;"}`;
      view.addEventListener("click", () => startEdit(i, "text"));

      if (showTitle()) body.append(title);
      body.append(view);
      return body;
    }

    const title = document.createElement("input");
    title.type = "text";
    title.value = item.title;
    title.placeholder = "제목";
    title.style.cssText =
      titleStyle +
      "flex-shrink:0;border:1px solid var(--border-color);background:var(--comfy-input-bg);outline:1px solid var(--input-text);";
    title.addEventListener("input", () => {
      items[i].title = title.value;
    });

    const textarea = document.createElement("textarea");
    textarea.value = item.text;
    textarea.rows = editLineCount(i);
    textarea.placeholder = "내용";
    textarea.style.cssText = boxStyle + "flex-shrink:0;resize:none;outline:1px solid var(--input-text);";
    textarea.addEventListener("input", () => {
      items[i].text = textarea.value;
      textarea.rows = editLineCount(i);
      refreshLabels();
    });

    // 제목은 1줄이라 Enter를 누르면 내용 입력창으로 넘어간다
    title.addEventListener("keydown", (e) => {
      if (e.key !== "Enter") return;
      e.preventDefault();
      textarea.focus();
    });

    // 제목과 내용 입력창 사이를 오갈 때는 편집을 유지하고, 항목 밖으로 나가면 보기 모드로 돌아간다
    const onBlur = (e) => {
      if (body.contains(e.relatedTarget)) return;
      editing = -1;
      render();
    };
    title.addEventListener("blur", onBlur);
    textarea.addEventListener("blur", onBlur);

    if (showTitle()) body.append(title);
    body.append(textarea);
    return body;
  };

  const render = () => {
    list.replaceChildren();
    items.forEach((item, i) => {
      const row = document.createElement("div");
      row.style.cssText = `display:flex;align-items:flex-start;gap:${GAP}px;flex-shrink:0;`;

      const label = document.createElement("span");
      label.style.cssText = `min-width:24px;text-align:right;opacity:0.7;font-size:12px;line-height:${TITLE_HEIGHT}px;`;
      label.dataset.label = "";

      const remove = createButton("✕", "항목 삭제", () => {
        items.splice(i, 1);
        if (items.length === 0) items.push(toItem(""));
        editing = -1;
        render();
      });
      remove.style.cssText = "width:24px;height:24px;flex-shrink:0;cursor:pointer;";

      row.append(label, createBody(item, i), remove);
      list.append(row);
    });
    refreshLabels();
    fitViewLines();
  };

  // 노드가 커질수록 목록이 스크롤 없이 다 들어가는 만큼 보기 모드 줄 수를 늘린다
  // 편집 중에는 다른 항목이 움직이지 않게 그대로 두고, 노드가 화면에 없어 높이가 0이면 건너뛴다
  const fitViewLines = () => {
    if (editing !== -1 || !list.clientHeight) return;
    const views = list.querySelectorAll("div[data-view]");
    const fits = (n) => {
      views.forEach((el) => el.style.setProperty("-webkit-line-clamp", String(n)));
      return list.scrollHeight <= list.clientHeight;
    };
    // 한 항목이 list 높이보다 많은 줄을 보일 수는 없으므로 그 줄 수까지만 이진 탐색한다
    let lo = MIN_VIEW_LINES;
    let hi = Math.max(lo, Math.floor(list.clientHeight / LINE_HEIGHT));
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      if (fits(mid)) lo = mid;
      else hi = mid - 1;
    }
    viewLines = lo;
    fits(viewLines);
  };
  // container 크기는 노드 크기로만 정해진다. list는 스크롤바가 생기고 사라질 때도 크기가 바뀌어 줄 수를 맞추다 다시 호출되므로 쓰지 않는다
  new ResizeObserver(fitViewLines).observe(container);

  const add = createButton("+ 항목 추가", "항목 추가", () => {
    items.push(toItem(""));
    startEdit(items.length - 1, showTitle() ? "title" : "text");
  });
  add.style.cssText = `height:${ADD_BUTTON_HEIGHT - 4}px;flex-shrink:0;cursor:pointer;`;
  container.append(add);

  const widget = node.addDOMWidget(inputName, "TEXT_LIST", container, {
    getValue: () => JSON.stringify(items),
    setValue: (value) => {
      items = parseValue(value);
      editing = -1;
      render();
    },
    // 최소 높이: 제목 + 2줄 내용 항목 하나 + 추가 버튼
    getMinHeight: () => TITLE_HEIGHT + 2 + MIN_VIEW_LINES * LINE_HEIGHT + ROW_PADDING + GAP + ADD_BUTTON_HEIGHT + 8,
  });

  widget.refreshIndexRange = refreshIndexRange;
  widget.render = render;
  render();
  return { widget };
}

app.registerExtension({
  name: "ComfyUI-Moon-Tools.TextList",
  getCustomWidgets() {
    return {
      TEXT_LIST: (node, inputName) => createTextListWidget(node, inputName),
    };
  },
  // TEXT_LIST 위젯이 만들어질 때는 index 위젯이 아직 없어서 노드 생성 후 한 번 더 맞춘다
  // show_title 위젯도 같은 이유로 여기서 연결하고, 워크플로를 불러와 값이 바뀐 뒤에도 다시 그린다
  nodeCreated(node) {
    const textList = node.widgets?.find((w) => w.type === "TEXT_LIST");
    if (!textList) return;
    textList.refreshIndexRange();

    const showTitle = node.widgets.find((w) => w.name === "show_title");
    if (showTitle) {
      const callback = showTitle.callback;
      showTitle.callback = function (...args) {
        const result = callback?.apply(this, args);
        textList.render();
        return result;
      };
    }
    const onConfigure = node.onConfigure;
    node.onConfigure = function (...args) {
      const result = onConfigure?.apply(this, args);
      textList.render();
      return result;
    };
    textList.render();
  },
});

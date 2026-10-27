# Context Notes

## 2026-10-22 결정 사항
- **ComfyUI-Text-List 구조를 그대로 따른다**: 커스텀 입력 타입(`IMAGE_LIST`) + `getCustomWidgets` DOM 위젯, index 위젯 범위 제한, Python 쪽 나머지 연산(순환), random On/Off + `IS_CHANGED` NaN.
- **저장 형식**: 업로드한 파일 이름들의 `JSON.stringify(items)` 문자열. 리스트 그대로 보내면 ComfyUI가 링크로 오인할 수 있다(Text List와 같은 이유).
  - 파일 이름은 기본 Load Image와 같은 형식이다. 하위 폴더가 있으면 `subfolder/name`, 위치는 ComfyUI `input` 폴더.
- **업로드**: ComfyUI 내장 `/upload/image` API를 쓴다. 파일 선택창에서 여러 장을 한 번에 고를 수 있다. 같은 이름 파일은 ComfyUI가 `(1)` 등을 붙여 새 이름으로 저장한다.
- **썸네일**: `/view?filename=...&type=input&subfolder=...` 로 불러온다.
- **출력**: IMAGE와 MASK. 기본 Load Image와 같이 알파 채널이 있으면 `1 - alpha`를 마스크로, 없으면 64×64 0 마스크를 낸다. 애니메이션 이미지는 첫 프레임만 쓴다.
- **빈 목록**: Text List는 빈 문자열을 냈지만 이미지는 "빈 이미지"가 없으므로 에러를 낸다.
- **캐시**: random Off일 때 `IS_CHANGED`는 선택된 파일 이름 + 수정 시각을 반환한다. 같은 이름의 파일이 덮어써지면 다시 실행된다.
- **folder_paths 지연 import**: ComfyUI 밖(단위 테스트)에서도 `nodes.py`를 import할 수 있도록 경로 해석 함수 안에서 import한다. 테스트는 `sys.modules`에 가짜 모듈을 넣는다.
- **노드 키 `ImageList`**: Text List(`TextList`)와 같은 방식으로 지었다. 다른 팩과 키가 겹치면 노드가 덮어써지므로, ComfyUI에서 노드 배지가 이 팩으로 나오는지 확인한다.
- **목록 UI**: 행 = 번호 | 썸네일(128px, 처음 64px에서 키움) + 파일 이름 | ✕. 목록은 노드 안에서 스크롤, 아래에 "+ 이미지 추가" 버튼 고정. 노드 자동 확장은 하지 않는다(Text List 최종 결정과 같음).

## 2026-10-22 drag and drop
- **두 경로**: 목록(DOM 위젯) 위 드롭은 컨테이너의 `drop` 이벤트로, 노드의 다른 영역(제목, index 위젯) 드롭은 LiteGraph `node.onDragOver`/`onDragDrop`으로 받는다. 업로드는 버튼과 같은 `addFiles`를 쓴다.
- **stopPropagation**: DOM 위젯 위 드롭이 document까지 올라가면 ComfyUI가 PNG를 워크플로로 불러오려 한다. 컨테이너에서 전파를 막는다.
- 이미지가 아닌 파일(`image/*`가 아님)은 건너뛴다. 드래그 중에는 목록에 점선 테두리를 표시한다.
- **2026-10-22 확인**: ComfyUI PC에서 처음엔 drag and drop과 128px 썸네일이 모두 반영되지 않았다. 코드 문제가 아니라 예전 `image_list.js`가 로드된 상태였고(업데이트/캐시), 최신으로 받은 뒤 둘 다 동작했다. 프론트엔드가 안 바뀐 것 같으면 `/extensions/ComfyUI-Moon-Image-List/image_list.js`를 직접 열어 버전부터 확인한다.

## 2026-10-27 nodes 폴더 구조
- **`nodes.py` → `nodes/image_list.py`**: 루트에 `nodes.py`와 `nodes/`가 함께 있으면 import 대상이 헷갈리므로 파일을 패키지 안으로 옮겼다. 노드마다 `nodes/<노드>.py` 파일 하나를 둔다.
- **등록은 루트 `__init__.py`에서 명시적으로**: 자동 탐색은 하지 않는다. 새 노드를 추가하면 루트 `__init__.py`에 import 1줄과 `NODE_CLASS_MAPPINGS`/`NODE_DISPLAY_NAME_MAPPINGS` 항목을 추가한다.
- **노드 키 유지**: `ImageList` 키와 표시 이름은 그대로라서 기존 워크플로는 영향이 없다.
- **ComfyUI 본체의 `nodes` 모듈과 이름이 같지만** 루트 `__init__.py`가 상대 import(`.nodes.image_list`)를 쓰므로 충돌하지 않는다. 노드 파일 안에서 ComfyUI 본체 `nodes`를 import해야 하면 절대 import(`import nodes`)가 본체를 가리키는지 확인한다.
- **테스트**: 노드별로 `tests/test_<노드>.py`. 기존 `tests/test_nodes.py`는 `tests/test_image_list.py`로 옮겼다.

## 2026-10-27 Any Index Switch
- **사용자 결정**: 입력 슬롯은 연결하면 자동 추가(고정 10개 대신), index는 Image List처럼 순환(에러 대신).
- **index 의미**: 연결된 value 입력을 슬롯 번호 순서로 센 뒤 `index % 개수`. 중간 슬롯이 비면 건너뛴다. 연결된 입력이 없으면 에러.
- **모든 타입**: `str`을 상속해 `__ne__`가 항상 False인 `AnyType("*")`을 입력/출력 타입으로 쓴다. 최신 ComfyUI `validate_node_input`은 `"*"`를 직접 받아 주지만, 예전 버전은 `!=` 비교만 하므로 호환용으로 남긴다.
- **동적 입력(백엔드)**: Python은 `value0`만 선언하고, `optional`을 `ValueInputs`(dict 하위 클래스)로 만들어 `value\d+` 이름이면 `in`/`[]`에 `(ANY, {"lazy": True})`로 답한다. ComfyUI 소스(master, 2026-10-27)로 확인한 근거는 다음과 같다.
  - `get_input_data`는 프롬프트에 있는 입력을 선언 여부와 관계없이 모두 함수에 넘긴다.
  - `graph.add_node`는 `get_input_info`로 lazy 여부를 판단하므로, 위 dict가 없으면 value1 이후 입력은 eager로 실행된다.
  - `validate_inputs`는 `set(optional)`, 즉 실제 키(value0)만 검증한다. value1 이후 입력의 업스트림은 이 노드를 거쳐 검증되지 않는다. 그 노드에 문제가 있으면 검증 단계가 아니라 실행할 때 에러가 난다(타입은 어차피 모두 허용).
  - 노드 정의 JSON은 dict의 실제 항목만 직렬화하므로 프론트엔드에는 value0만 보인다.
- **지연 평가**: `check_lazy_status`는 선택된 입력이 아직 None(미실행)일 때만 그 이름을 돌려준다. ComfyUI가 이미 실행된 입력은 걸러 주므로 무한 대기는 없다.
- **동적 입력(프론트엔드)**: `onConnectionsChange`에서 슬롯을 맞춘다. 끝에서만 추가/삭제해 이름이 value0부터 빈틈없이 이어지게 한다. 중간 빈 슬롯은 지우지 않는다. 링크를 같은 노드의 다른 슬롯으로 옮기면 끊기→연결이 연달아 일어나 중간에 슬롯을 지우면 대상 슬롯이 사라질 수 있으므로 `queueMicrotask`로 미룬다. 불러온 워크플로는 이미 정리된 모양이라 맞추기가 아무것도 바꾸지 않고, 노드 크기도 바뀔 때만 높이를 다시 맞춘다.
- **V3 스키마(`io.Autogrow`)는 쓰지 않았다**: 최신 ComfyUI에는 동적 입력 기능이 있지만, 이 팩은 V1 방식이고 ComfyUI 밖 단위 테스트를 유지하려고 기존 방식을 따른다.
- **노드 키 `AnyIndexSwitch`**: Image List와 같은 규칙(접두사 없음, 표시 이름에 키 표기).

## 2026-10-27 저장소 이름 변경
- **새 이름**: `ComfyUI-Moon-Tools` (사용자가 GitHub Settings에서 변경). 옛 주소 `ComfyUI-Moon-Image-List`는 301로 새 주소에 연결되고, 새 저장소의 main이 로컬 origin/main(d860827)과 같은 것을 확인했다.
- **이유**: Text List를 합쳐 여러 노드를 담는 팩이 되므로(아래 "Text List 통합").
- **바꾼 곳**: README 제목·clone 주소, 프론트엔드 확장 이름(`ComfyUI-Moon-Tools.ImageList`, `ComfyUI-Moon-Tools.AnyIndexSwitch`), 로컬 `origin` 주소.
- **바꾸지 않은 곳**: 노드 키·표시 이름(워크플로 호환), Image List 드래그 MIME 타입(`application/x-comfyui-moon-image-list-item`, 위젯 내부 식별자), 로컬 폴더 이름.
- **확장 이름 변경 영향**: 이 확장들은 설정을 저장하지 않아 잃는 값이 없다. ComfyUI 설정에서 확장을 꺼 두었다면 다시 켜진 상태가 된다(Text List 때와 같은 판단).
- **프론트엔드 파일 경로**: ComfyUI는 `/extensions/<설치 폴더 이름>/...`으로 JS를 제공한다. 위 "drag and drop" 기록의 `/extensions/ComfyUI-Moon-Image-List/image_list.js`는 설치 폴더 이름을 따르므로, 새로 clone했다면 `/extensions/ComfyUI-Moon-Tools/image_list.js`다.

## 2026-10-27 Text List 통합
- **가져온 것**: ComfyUI-Moon-Text-List의 마지막 커밋 1d8775a에서 `nodes.py` → `nodes/text_list.py`, `web/text_list.js`, `tests/test_nodes.py` → `tests/test_text_list.py`. 코드는 그대로이고, 바꾼 곳은 테스트 import 경로와 확장 이름(`ComfyUI-Moon-Tools.TextList`)뿐이다.
- **git 이력은 가져오지 않았다**: 파일만 복사했다. 이전 이력은 GitHub의 ComfyUI-Moon-Text-List 저장소에 남는다. 이력까지 합치려면 나중에 `git merge --allow-unrelated-histories`로 붙일 수 있다.
- **노드 키·표시 이름 유지**: `TextList` / `Text List`. 저장된 워크플로가 그대로 열린다. Image List·Any Index Switch와 표시 이름 규칙(`Moon ... (Key)`)이 다르지만, 노드 제목이 바뀌는 변경이라 통합 범위 밖으로 두었다.
- **예전 팩과 함께 설치하면 안 된다**: 같은 `TextList` 키가 두 번 등록되면 나중에 불러온 쪽이 덮어쓴다. 두 JS 확장이 모두 `TEXT_LIST` 위젯과 `nodeCreated`를 등록해 위젯 이벤트가 두 번 붙을 수 있다. README에 예전 폴더를 지우라고 적었다.
- **중복 코드는 합치지 않았다**: `parse_items`, `_rng`가 `image_list.py`와 `text_list.py`에 각각 있지만 형식(파일 이름 목록 / 제목·내용 쌍)이 달라 모듈마다 둔다.
- **README**: 이 저장소의 한국어 README.md 하나에 Text List 사용법(README.ko.md 기준)을 넣었다. Text List의 영어 README는 가져오지 않았다.
- **Text List 기록**: 아래에 원래 context-notes를 그대로 붙였다. 파일 이름은 통합 전 기준이다(`nodes.py` = 지금의 `nodes/text_list.py`).
- **README 팁 주의**: Text List 기록("GitHub 공개용 README + 라이선스")에 따르면 프론트엔드는 `control_after_generate` 옵션이 있거나 이름이 `seed`/`noise_seed`인 INT에만 control after generate를 붙인다. Image List README의 `index` increment 팁은 이 기준으로는 동작하지 않을 수 있다. 사용자 확인이 필요하다.

## 2026-10-27 Moon Save Image 통합
- **가져온 것**: ComfyUI-Moon-SaveImage의 마지막 커밋 596bb94에서 `nodes.py` → `nodes/save_image.py`, `tests/test_nodes.py` → `tests/test_save_image.py`. 노드 코드는 그대로다. 프론트엔드 JS는 원래 없다.
- **테스트에서 바꾼 곳**: import 경로, 그리고 가짜 `folder_paths`를 `addCleanup`으로 되돌리는 한 줄. `test_image_list.py`는 import할 때 가짜 모듈을 한 번 넣고, Save Image 테스트는 `setUp`마다 덮어쓴다. discover는 알파벳 순서라 Image List가 먼저 돌아 통과하지만, Save Image 테스트를 먼저 실행하면(`python -m unittest tests.test_save_image tests.test_image_list`) Image List 테스트 4개가 `get_annotated_filepath` 없음으로 실패하는 것을 확인했다. `mock.patch.dict(sys.modules)`는 끝날 때 sys.modules 전체를 되돌려 테스트 중에 import된 PIL 플러그인 모듈까지 지우므로 쓰지 않았다.
- **가져오지 않은 것**: `.vscode/settings.json`(VS Code unittest 탐색 설정). 이 저장소에는 지금까지 편집기 설정을 두지 않았다. git 이력도 Text List처럼 가져오지 않았다. 이전 이력은 GitHub의 ComfyUI-Moon-SaveImage 저장소에 남는다.
- **노드 키·표시 이름·카테고리 유지**: `MoonSaveImage` / `Moon Save Image (MoonSaveImage)` / `image`. 다른 노드와 달리 키에 `Moon` 접두어가 있는 이유는 아래 Save Image 기록 참고(기본 `SaveImage`와 겹침).
- **예전 팩과 함께 설치하면 안 된다**: 같은 `MoonSaveImage` 키가 두 번 등록되어 나중에 불러온 쪽이 덮어쓴다. JS가 없어 위젯이 두 번 붙는 문제는 없지만, 예전 쪽이 이기면 이 저장소의 수정이 반영되지 않는다. README에 예전 폴더를 지우라고 적었다.
- **보안 섹션을 팩 수준으로 올렸다**: 이 팩의 다른 노드는 파일을 쓰지 않았지만, Save Image는 output 밖 저장을 허용한다. 팩을 설치하면 이 기능도 함께 들어오므로 README에 `## 보안`을 따로 두었다.
- **README**: Text List 때와 같이 한국어 README.md 하나에 README.ko.md 내용을 넣었다. 영어 README는 가져오지 않았다. 설치·업데이트·삭제 안내는 팩 공통 내용과 겹쳐 뺐다.
- **Save Image 기록**: 아래에 원래 context-notes를 그대로 붙였다. 파일 이름은 통합 전 기준이다(`nodes.py` = 지금의 `nodes/save_image.py`).

## 2026-10-27 저장소 설명 갱신
- **GitHub About**: Image List 시절 문구("manage multiple images as a list and output one by index or random")가 남아 있었다. 새 문구는 `ComfyUI custom nodes: image and text lists that output one item by index or random, an any-type index switch, and an image saver with format, folder, and metadata options`. 이 PC에는 `gh`·인증이 없어 사용자가 Settings에서 직접 바꾼다.
- **README 첫 문단**: 위 문구와 같은 순서(목록 → 스위치 → 저장)로 네 노드를 모두 소개한다. 이전 문단에는 Any Index Switch가 빠져 있었다.
- **노드 검색 안내**: 세 노드는 표시 이름에 `Moon`이 있고 Text List는 `SEARCH_ALIASES`의 `moon`으로 찾히므로, 문제 해결에서는 `moon` 하나로 안내한다. 별칭을 지원하지 않는 예전 ComfyUI(bdeac88 이전)에서는 Text List만 `text list`로 찾아야 한다.

## Text List (ComfyUI-Moon-Text-List에서 통합)

### 2026-10-21 결정 사항
- **항목 구분**: 줄바꿈 기준. 각 줄은 앞뒤 공백을 제거하고, 빈 줄은 항목에서 제외한다.
  - 이유: 프롬프트 목록을 위젯에 붙여 넣을 때 빈 줄이 섞이기 쉽다.
- **index 범위 초과**: 항목 수로 나눈 나머지를 사용한다(순환).
  - 이유: index 위젯을 `increment`로 두면 큐를 돌릴 때마다 목록을 끝없이 순환할 수 있다.
- **빈 목록**: 에러 대신 빈 문자열을 출력한다.
- **테스트**: pytest가 설치되어 있지 않아 표준 `unittest`를 사용한다. `python -m unittest` 로 실행.
- **배포**: 개인용이므로 `pyproject.toml`/Registry 설정은 만들지 않는다.

### 2026-10-21 항목별 입력칸 UI
- **방식**: 커스텀 입력 타입 `TEXT_LIST` + 프론트엔드 `getCustomWidgets`로 DOM 위젯을 만든다.
  - 이유: 기본 STRING 위젯을 숨기는 방식은 프론트엔드 버전(캔버스/Vue 노드)마다 동작이 달라 깨지기 쉽다.
- **저장 형식**: 항목들을 줄바꿈으로 이어 붙인 문자열. 입력칸은 한 줄짜리라 항목 안에 줄바꿈이 들어갈 일이 없다.
  - 리스트 그대로 보내면 ComfyUI가 `[node_id, slot]` 링크로 오인할 수 있어 문자열로 보낸다.
  - Python 선택 로직(`parse_items`)과 기존 테스트를 그대로 쓸 수 있다.
- **빈 항목**: Python에서 계속 제외한다. UI의 번호도 비어 있지 않은 항목만 세고, 빈 칸은 `-`로 표시해 실제 index와 맞춘다.
- **주의**: ComfyUI에 표시된 노드 배지가 `comfyui-workflow-encrypt`였다. 다른 팩과 `TextList` 키가 충돌했을 가능성이 있어 확인이 필요하다.

### 2026-10-21 랜덤 On/Off
- **On일 때 index는 무시**하고 비어 있지 않은 항목 중 하나를 고른다.
- **재실행**: ComfyUI는 입력이 같으면 캐시된 결과를 쓴다. On일 때 `IS_CHANGED`가 NaN을 반환해 매번 다시 실행되게 한다. Off일 때는 일정한 값을 반환해 캐시를 그대로 쓴다.
- **난수 생성기**: 모듈 전용 `random.Random()` 인스턴스를 쓴다. 다른 노드가 전역 `random.seed()`를 고정해도 같은 값이 반복되지 않게 하기 위해서다.
- **seed 위젯을 쓰지 않은 이유**: 요청이 단순 On/Off였다. 결과 재현이 필요해지면 seed 입력(control_after_generate)으로 바꾸는 것을 검토한다.

### 2026-10-21 index 범위 제한
- **화살표 제한**: index 위젯의 `options.max`를 항목이 바뀔 때마다 갱신한다. 순환이 아니라 끝에서 멈춘다.
- **갱신 시점**: TEXT_LIST 위젯이 만들어질 때는 index 위젯이 아직 없어서 `nodeCreated`에서 한 번 더 맞춘다.
- **Python의 나머지 연산은 유지**: index를 다른 노드에서 링크로 받으면 UI 제한이 적용되지 않으므로 안전장치로 둔다.

### 2026-10-21 보기/편집 전환 + 항목 내 줄바꿈
- **편집 단위**: 클릭한 항목 하나만 textarea로 바뀐다. 포커스를 잃으면 보기 모드로 돌아간다.
- **저장 형식 변경**: 항목 안에 줄바꿈이 들어가므로 줄 단위 문자열 대신 `JSON.stringify(items)` 문자열로 보낸다.
  - 리스트 자체가 아니라 문자열이라 ComfyUI가 링크로 오인하지 않는다.
  - JSON 배열이 아니면 예전 형식으로 보고 줄 단위로 나눈다(Python, JS 모두).
- **버튼 mousedown preventDefault**: 편집 중 삭제/추가 버튼을 누르면 textarea blur → 다시 그리기로 버튼이 사라져 click이 유실된다. 포커스 이동을 막아 해결.
- **높이 계산**: 실제 DOM 높이 대신 줄 수 × 줄 높이로 추정한다. 긴 줄이 자동 줄바꿈되면 모자랄 수 있어 컨테이너에 `overflow-y:auto`를 둔다.

### 2026-10-21 입력창 최대 10줄
- 편집 중인 textarea의 표시 줄 수를 최대 10줄(`MAX_EDIT_LINES`)로 제한한다. 넘으면 textarea 안에서 스크롤한다.
- 보기 모드는 제한하지 않는다(요청이 입력창 한정).

### 2026-10-21 보기 모드 최대 2줄
- 보기 모드 항목은 최대 2줄(`MAX_VIEW_LINES`)만 보이고 나머지는 `-webkit-line-clamp`로 `…` 처리한다.
- 이전에는 보기 모드 높이 제한이 없어, 편집을 마쳐도 항목 줄 수만큼 높이가 유지됐다.
- 높이 추정도 보기 모드는 최대 2줄로 계산해, 편집을 마치면 노드가 다시 줄어든다.

### 2026-10-21 목록 스크롤 + 노드 높이 고정
- **자동 확장 제거**: 항목 추가/편집 때 `node.setSize`로 노드를 키우던 동작을 없앴다. 노드 높이는 사용자가 정한 대로 둔다.
- **구조**: 컨테이너(height:100%) = 스크롤되는 list(flex:1, overflow-y:auto) + 아래 고정된 "+ 항목 추가" 버튼.
- **최소 높이**: 2줄 항목 하나 + 추가 버튼(`getMinHeight` 고정값 90px).
- 편집 입력창(최대 10줄)이 list보다 크면 list가 스크롤된다. 새 항목은 focus 시 브라우저가 보이는 위치로 스크롤한다.

### 2026-10-22 항목 제목
- **저장 형식**: 항목 = `{ title, text }`, 전체는 `JSON.stringify(items)`. 문자열 항목(예전 형식)은 `{ title: "", text }`로 읽는다(Python `item_text`, JS `toItem`).
- **출력은 내용만**: 제목은 목록에서 항목을 구분하는 용도. 출력 슬롯은 그대로 하나다.
- **빈 항목 판정은 내용 기준**: 제목만 있고 내용이 비면 빈 항목으로 보고 index 번호에서 뺀다(`-` 표시).
- **편집 전환**: 제목 label을 누르면 제목 입력창에, 내용을 누르면 내용 입력창에 포커스. blur 때 `relatedTarget`이 같은 항목 안이면 편집을 유지해 제목↔내용을 오갈 수 있게 했다.
- **제목 Enter**: 1줄 입력이라 Enter는 내용 입력창으로 이동한다.
- **새 항목**: `+ 항목 추가` 시 제목 입력창부터 포커스한다.
- **확인 방법**: ComfyUI가 이 PC에 없어 jsdom으로 위젯을 띄워 전환/저장 동작을 확인했다(임시 스크립트, 저장소에는 넣지 않음).

### 2026-10-22 제목 숨김
- **범위**: 노드 전체 토글. 항목별 숨김은 하지 않는다.
- **위치**: `random`처럼 `show_title` BOOLEAN 위젯(사용자 선택). Python은 인자만 받고 쓰지 않는다. 예전 워크플로는 기본값 On으로 채워진다.
- **편집 때도 숨김**: Off면 편집 모드에서도 내용 입력창만 보인다. 제목 데이터는 지우지 않아 다시 켜면 돌아온다.
- **다시 그리기 시점**: TEXT_LIST 위젯이 만들어질 때 `show_title` 위젯이 아직 없어서 `nodeCreated`에서 위젯 callback과 `node.onConfigure`(워크플로 불러오기)에 render를 연결한다.

### 2026-10-22 title 출력
- **슬롯 순서**: `(text, title)`. text를 첫 슬롯에 두어 기존 워크플로의 링크가 그대로 이어진다.
- **파싱**: `parse_items`가 `(제목, 내용)` 쌍을 돌려준다. 둘 다 앞뒤 공백을 제거한다. 빈 항목 판정은 여전히 내용 기준이다.
- **제목 없음**: 예전 문자열 항목, `title` 키가 없거나 빈 경우 모두 빈 문자열. 빈 목록이면 둘 다 빈 문자열.
- **show_title과 무관**: 이 위젯은 UI 표시만 정한다. Off여도 `title`은 출력한다(사용자 요청). "출력은 내용만"이던 2026-10-22 항목 제목 결정은 이걸로 바뀌었다.

### 2026-10-22 text_list 출력
- **형식**: ComfyUI 표준 리스트 출력(`OUTPUT_IS_LIST = (False, False, True)`), 타입은 STRING. 연결된 일반 노드는 항목마다 한 번씩 실행된다. 하나의 Python list를 STRING 슬롯으로 보내면 받는 노드가 문자열로 다루다 깨지므로 쓰지 않았다.
- **내용**: 선택과 같은 기준(빈 내용 제외, 앞뒤 공백 제거)으로 모든 항목의 내용만 보낸다. 제목은 넣지 않는다. index/random과 무관하다.
- **슬롯 순서**: `(text, title, text_list)`. 기존 링크 유지.

### 2026-10-22 title_list 출력
- **범위**: UI에서 번호가 붙는 항목(내용이 비지 않은 항목)만 넘긴다(사용자 확인). text_list와 같은 기준이라 두 리스트의 길이와 순서가 같다.
- **제목 없음**: 빈 문자열로 자리를 채워 text_list와 짝이 맞게 한다.
- **슬롯 순서**: `(text, title, text_list, title_list)`.

### 2026-10-22 출력 슬롯 순서 변경
- **순서**: `(title, text, title_list, text_list)` (사용자 요청). 이전의 "text를 첫 슬롯에 두어 기존 링크 유지" 결정은 이걸로 바뀌었다.
- **영향**: ComfyUI 링크는 슬롯 번호로 저장되므로, 예전에 저장한 워크플로는 이 노드의 출력 링크를 다시 연결해야 한다.

### 2026-10-26 보기 모드 줄 수 자동 확장
- **규칙**: 모든 항목에 같은 줄 수 N을 쓴다. 5줄부터 줄여 가며 목록이 스크롤 없이 다 들어가는 가장 큰 N을 고르고, 2줄로도 넘치면 2줄(예전 동작) + 스크롤. "보기 모드 최대 2줄" 결정은 이걸로 바뀌었다.
  - 항목별로 다르게 늘리는 방식은 어느 항목을 먼저 늘릴지 정해야 해서 쓰지 않았다.
- **측정**: 줄 수 추정 대신 `list.scrollHeight <= list.clientHeight`를 실제로 재본다. 긴 줄이 자동 줄바꿈된 경우도 맞게 계산된다.
- **다시 맞추는 시점**: render 끝, container의 ResizeObserver(노드 크기 변경). list를 관찰하면 스크롤바가 생기고 사라질 때마다 list 너비가 바뀌어 줄 수를 맞추다 다시 호출되므로 container를 관찰한다.
- **편집 중에는 유지**: 편집 입력창이 커져도 다른 항목 줄 수가 바뀌어 화면이 움직이지 않게 한다. blur 후 render에서 다시 맞춘다.
- **높이 0이면 건너뜀**: 노드가 접히거나 화면에 없을 때 0 ≤ 0으로 5줄을 고르지 않게 한다.
- **최소 높이**: `getMinHeight`는 계속 2줄 기준.
- **확인 방법**: 헤드리스 Chrome(CDP, 실제 시간)으로 위젯을 띄워 확인했다. `--virtual-time-budget` 모드는 렌더링 프레임이 돌지 않아 ResizeObserver가 호출되지 않으므로 쓸 수 없었다.

### 2026-10-26 줄 수 상한 제거
- **변경**: 최대 5줄 제한을 없앴다(사용자 요청: 노드 높이가 커질수록 줄 수도 늘리기). 위 "5줄부터 줄여 가며" 규칙은 이걸로 바뀌었다.
- **탐색**: 상한이 없어 한 줄씩 줄이면 큰 노드에서 수십 번 레이아웃을 잰다. 2줄 ~ `list 높이 / LINE_HEIGHT` 사이를 이진 탐색한다. 한 항목이 list보다 많은 줄을 보일 수 없으므로 이 값이 상한이다. 줄 수가 늘면 높이도 줄지 않으므로 이진 탐색이 맞다.
- **결과**: 노드를 키우면 내용이 다 보일 때까지 줄 수가 늘고, 줄이면 다시 줄어든다. 2줄로도 넘치면 예전처럼 2줄 + 스크롤.

### 2026-10-27 노드 검색 별칭
- **방식**: 노드 클래스에 `SEARCH_ALIASES` 리스트를 둔다. ComfyUI `server.py`가 이를 `search_aliases`로 내보내고, 프론트엔드 노드 검색(Fuse.js)은 `name`, `display_name`, `search_aliases`를 키로 찾는다(2026-10-27 기준 master/main 소스 확인).
- **별칭**: `moon`, `text`, `textlist`, `text list` (사용자 요청). `moon` 외에는 이미 name(`TextList`)이나 display_name(`Text List`)으로 찾히지만, 요청한 검색어를 한곳에 명시하려고 모두 넣었다.
- **display_name을 "Moon Text List"로 바꾸지 않은 이유**: 노드 제목이 바뀌는 눈에 보이는 변경이라 요청 범위를 넘는다. 별칭을 지원하지 않는 예전 ComfyUI에서 `moon` 검색이 필요해지면 그때 검토한다.
- **노드 키(`TextList`)는 그대로**: 바꾸면 저장된 워크플로가 노드를 찾지 못한다.
- **지원 시점**: ComfyUI 커밋 bdeac88(2026-01-21, #12010)에서 `SEARCH_ALIASES`가 추가됐다. 그 전 버전에서는 `moon`으로 찾히지 않는다.

### 2026-10-27 GitHub 공개용 README + 라이선스
- **라이선스: MIT** (사용자 선택). 근거로 조사한 내용은 다음과 같다.
  - ComfyUI 본체·ComfyUI_frontend는 GPL-3.0.
  - 인기 노드는 나뉜다. MIT(Custom-Scripts, rgthree, essentials, WAS), GPL-3.0(KJNodes, Impact Pack, Easy-Use), Apache-2.0(use-everywhere, controlnet_aux).
  - Comfy Registry의 `pyproject.toml` 규격에서 `license`는 선택 항목이고, `{ file = "LICENSE" }` 형식을 쓴다.
  - 이 노드의 Python은 ComfyUI 코드를 import하지 않는다. JS만 실행 시점에 `../../scripts/app.js`를 import하며, MIT인 rgthree·Custom-Scripts도 같은 방식이다.
  - LICENSE가 없으면 기본적으로 모든 권리가 저작자에게 있어 다른 사람이 쓸 수 없다. 공개하려면 필요했다.
  - 저작권자 이름은 git 사용자명 `javamoon71`.
- **README 언어**: 영어 `README.md` + 한국어 `README.ko.md` (사용자 선택). 맨 위에서 서로 링크한다.
- **구성**: 인기 노드 README(rgthree, Custom-Scripts, Impact Pack, KJNodes)를 참고해 소개 → 기능 → 설치(git clone, Manager, 업데이트, 삭제) → 사용법(입출력 표, 세부 동작) → 개발 → 라이선스 순으로 정리했다.
- **ComfyUI-Manager 설치**: 아직 Manager 목록/Registry에 등록하지 않아 "Install via Git URL"만 안내한다. 최근 Manager는 `config.ini`의 `allow_git_url_install = true`(기본값 false)가 있어야 허용한다.
- **UI 문구**: 위젯 버튼·placeholder가 한국어라 영어 README에 문구와 뜻을 표로 붙였다. UI 번역은 요청 범위 밖이라 하지 않았다.
- **`control after generate` 팁 삭제**: ComfyUI 프론트엔드(`useIntWidget.ts`)는 `control_after_generate` 옵션이 있거나 이름이 `seed`/`noise_seed`인 INT에만 이 컨트롤을 붙인다. `index`에는 없어서 예전 README의 팁은 동작하지 않았다.
- **클론 주소**: GitHub 저장소 이름은 `ComfyUI-Text-List`다(로컬 폴더 이름 `ComfyUI-Moon-Text-List`와 다름). README의 설치·업데이트 경로는 GitHub 이름을 따른다. → 아래 "저장소 이름 변경"으로 바뀌었다.

### 2026-10-27 저장소 이름 변경
- **새 이름**: `ComfyUI-Moon-Text-List` (사용자 요청). 로컬 폴더 이름과 같아졌다.
- **바꾼 곳**: README 두 파일의 제목(`ComfyUI Moon Text List`), clone 주소, 설치 폴더 경로. 프론트엔드 확장 이름 `ComfyUI-Moon-Text-List.TextList`. 로컬 `origin` 주소.
- **바꾸지 않은 곳**: 노드 키 `TextList`, 표시 이름 `Text List`, 카테고리. 저장소 이름이 아니라 노드 이름이고, 키를 바꾸면 저장된 워크플로가 깨진다.
- **확장 이름 변경 영향**: 확장 이름은 ComfyUI 안에서 확장을 구분하는 식별자다. 이 확장은 설정을 저장하지 않아 바꿔도 잃는 값이 없다. 사용자가 ComfyUI 설정에서 이 확장을 꺼 두었다면 다시 켜진 상태가 된다.
- **GitHub 쪽**: 이 PC에 GitHub CLI·인증이 없어 저장소 이름 변경은 사용자가 Settings에서 한다. GitHub는 옛 주소를 새 주소로 자동 연결하므로 기존 설치본의 `git pull`도 계속 된다. 옛 이름으로 새 저장소를 만들면 이 연결이 끊긴다.
- **기존 설치본**: 폴더 이름이 `ComfyUI-Text-List`로 남아도 동작한다. `WEB_DIRECTORY`가 상대 경로이고 JS도 `../../scripts/app.js`로 폴더 이름에 의존하지 않는다.

## Moon Save Image (ComfyUI-Moon-SaveImage에서 통합)
통합 전 저장소의 기록이다(마지막 커밋 596bb94). 파일 이름은 통합 전 기준이다.

### 2026-10-27 결정 사항
- **참고한 노드**: ComfyUI 기본 `SaveImage`(파일 이름 규칙, PNG 메타데이터, `ui.images` 미리보기), `SaveAnimatedWEBP`(WebP EXIF 메타데이터 형식), WAS `Image Save`(경로·형식·quality 옵션).
- **노드 키 `MoonSaveImage`**: 다른 Moon 노드처럼 짧은 키를 쓰면 기본 노드 `SaveImage`와 겹쳐 덮어쓴다. 그래서 `Moon` 접두어를 붙였다.
- **파일 이름**: 기본 SaveImage와 같은 `{prefix}_{counter:05}_.{ext}`. 번호는 폴더 안 같은 prefix 파일 중 가장 큰 번호 + 1이고, 형식(png/jpg/webp)과 상관없이 이어진다. `folder_paths.get_save_image_path`는 output 폴더 밖 저장을 막기 때문에 쓰지 않고 같은 규칙을 직접 구현했다.
- **치환 토큰**: 기본 SaveImage의 `%date:yyyy-MM-dd%`는 프론트엔드가 정해진 노드(SaveImage 등)에만 적용한다. 커스텀 노드에는 적용되지 않으므로 Python에서 같은 형식(yyyy, yy, MM, M, dd, d, hh, h, mm, m, ss, s)으로 바꾼다. 서버 쪽 기본 토큰 중 `%width%`, `%height%`도 지원한다. `%노드이름.위젯%`은 지원하지 않는다.
- **저장 경로**: `os.path.join(output, output_path, filename_prefix)`. output_path가 절대 경로면 그 위치, 상대 경로면 output 기준. filename_prefix 안의 하위 폴더(`sub/name`)도 기본 노드처럼 동작한다. 폴더는 자동 생성한다. 절대 경로를 허용하므로 공유 서버에서는 ComfyUI 프로세스가 쓸 수 있는 어디든 저장된다(README에 적음).
- **메타데이터**: png는 기본 SaveImage처럼 텍스트 청크(`prompt`, `workflow`). webp는 SaveAnimatedWEBP처럼 EXIF `0x0110`=`prompt:{json}`, `0x010f`부터 내려가며 `workflow:{json}`. jpg는 넣지 않는다. JPEG EXIF는 64KB 제한이 있어 큰 워크플로가 저장 오류를 내기 때문이다(WAS도 jpg에는 넣지 않음). ComfyUI `--disable-metadata` 플래그는 보지 않고 노드의 On/Off만 따른다.
- **jpg 알파**: RGBA(4채널) IMAGE가 들어오면 jpg만 RGB로 바꿔 저장한다.
- **미리보기**: output 폴더 안에 저장하면 그 파일을 `type: output`으로 보여 준다. output 밖(절대 경로, `..`)이면 `/view`로 열 수 없어서 temp 폴더에 png 사본을 저장해 `type: temp`로 보여 준다(PreviewImage와 같은 방식, temp는 ComfyUI 시작 시 비워짐).
- **출력**: 저장 후 입력 IMAGE를 그대로 내보내 다음 노드로 이을 수 있다. `OUTPUT_NODE = True`라서 출력을 연결하지 않아도 실행된다.
- **folder_paths 지연 import**: Image List와 같은 이유. 테스트는 `sys.modules`에 가짜 모듈을 넣는다.

### 2026-10-27 GitHub 공개 준비
- **README 구성**: Text-List와 같이 영어 `README.md`를 기본으로, 한국어 `README.ko.md`를 따로 둔다. 설치(git clone, ComfyUI-Manager Git URL), 업데이트, 삭제, 입력/출력 표, 토큰, 형식별 메타데이터, 세부 동작 순서다.
- **보안 섹션**: 기본 SaveImage와 달리 output 밖 저장을 허용하므로 공개 README에 따로 적었다.
- **라이선스**: Moon 노드들과 같은 MIT, `Copyright (c) 2026 javamoon71`. 작업 폴더의 LICENSE가 CRLF여도 `core.autocrlf=true`라 저장소에는 LF로 커밋된다(`git show HEAD:LICENSE`로 확인). 따로 고칠 필요 없다.
- **ComfyUI(GPL-3.0) 참고 범위**: 기본 노드의 동작 규칙(파일 이름 형식, PNG 텍스트 청크·WebP EXIF 키 배치, `ui.images` 형식)을 맞췄을 뿐 코드를 복사하지 않았다. 대부분의 커스텀 노드처럼 MIT로 배포한다.

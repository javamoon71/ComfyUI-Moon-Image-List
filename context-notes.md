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

# Checklist

## Plan
여러 장의 이미지를 목록으로 관리하고, index(또는 랜덤)에 해당하는 이미지 하나를 출력하는 ComfyUI 커스텀 노드. ComfyUI-Text-List의 이미지 버전.
- 입력: images(IMAGE_LIST 위젯, 업로드한 파일 이름 목록), index(INT, 0부터), random(On/Off)
- 출력: IMAGE, MASK (기본 Load Image 노드와 같은 형식)

## Tasks
- [x] 프로젝트 폴더 생성, git 초기화
- [x] 선택/로드 로직 구현 (`nodes.py`)
- [x] ComfyUI 등록 (`__init__.py`)
- [x] 썸네일 목록 + 업로드/삭제 위젯 (`web/image_list.js`)
- [x] 단위 테스트 작성 및 통과 (`tests/test_nodes.py`)
- [x] README 작성
- [x] 커밋
- [x] GitHub 저장소 생성 및 push
- [ ] ComfyUI PC에서 실제 동작 확인

## Plan 2 — drag and drop 추가
- [x] 목록 위에 놓은 이미지 파일 업로드 (ComfyUI 기본 드롭 처리 막기)
- [x] 노드의 다른 영역에 놓아도 추가 (`onDragOver`/`onDragDrop`)
- [x] README 반영
- [x] ComfyUI PC에서 실제 동작 확인

## Plan 3 — nodes 폴더로 구조 변경
여러 노드를 추가할 수 있도록 노드 파일을 `nodes/` 패키지로 모은다.
- [x] `nodes.py` → `nodes/image_list.py` 이동, `nodes/__init__.py` 추가
- [x] 루트 `__init__.py` import 경로 수정
- [x] 테스트를 `tests/test_image_list.py`로 이동, import 수정
- [x] 테스트 통과 확인
- [ ] ComfyUI PC에서 노드가 그대로 로드되는지 확인

## Plan 4 — Any Index Switch 노드
어떤 타입이든 여러 입력(value0, value1, ...)을 받아 index에 해당하는 값 하나를 출력한다.
- 입력: index(INT), value0~(모든 타입, 연결하면 다음 슬롯 자동 추가)
- 출력: value(모든 타입)
- index는 연결된 입력을 슬롯 순서대로 세어 순환한다. 선택된 입력만 실행한다(lazy).
- [x] 노드 구현 (`nodes/any_index_switch.py`)
- [x] 슬롯 자동 추가/정리 (`web/any_index_switch.js`)
- [x] 등록 (`__init__.py`)
- [x] 단위 테스트 (`tests/test_any_index_switch.py`)
- [x] README 반영
- [ ] ComfyUI PC에서 실제 동작 확인

## Plan 5 — 저장소 이름 변경 (ComfyUI-Moon-Image-List → ComfyUI-Moon-Tools)
- [x] GitHub 저장소 이름 변경 (사용자가 직접), 옛 주소 301 연결 확인
- [x] README 제목, clone 주소 변경
- [x] 프론트엔드 확장 이름 `ComfyUI-Moon-Tools.*`로 변경
- [x] 로컬 git remote 주소 변경

## Plan 6 — Text List 통합 (ComfyUI-Moon-Text-List → nodes)
- [ ] `nodes/text_list.py`, `web/text_list.js`, `tests/test_text_list.py` 가져오기 (원본 1d8775a)
- [ ] 등록 (`__init__.py`), 노드 키 `TextList`와 표시 이름 유지
- [ ] README에 Text List 사용법과 예전 저장소에서 옮겨 오는 방법 추가
- [ ] Text List의 checklist / context-notes 이어 붙이기
- [ ] 테스트 + 패키지 로드 + JS 문법 검사
- [ ] GitHub `ComfyUI-Moon-Tools`에 push
- [ ] ComfyUI PC: 예전 `ComfyUI-Moon-Text-List` 폴더 삭제 후 세 노드 동작 확인

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
- [x] `nodes/text_list.py`, `web/text_list.js`, `tests/test_text_list.py` 가져오기 (원본 1d8775a)
- [x] 등록 (`__init__.py`), 노드 키 `TextList`와 표시 이름 유지
- [x] README에 Text List 사용법과 예전 저장소에서 옮겨 오는 방법 추가
- [x] Text List의 checklist / context-notes 이어 붙이기
- [x] 테스트 + 패키지 로드 + JS 문법 검사
- [x] GitHub `ComfyUI-Moon-Tools`에 push, 새 주소로 clone 후 테스트 통과 확인
- [ ] ComfyUI PC: 예전 `ComfyUI-Moon-Text-List` 폴더 삭제 후 세 노드 동작 확인

## Plan 7 — Moon Save Image 통합 (ComfyUI-Moon-SaveImage → nodes)
- [x] `nodes/save_image.py`, `tests/test_save_image.py` 가져오기 (원본 596bb94)
- [x] 테스트의 가짜 `folder_paths`를 테스트가 끝나면 되돌리기 (Image List 테스트와 충돌 방지)
- [x] 등록 (`__init__.py`), 노드 키 `MoonSaveImage`와 표시 이름 유지
- [x] README에 Moon Save Image 사용법, 보안 주의, 예전 저장소에서 옮겨 오는 방법 추가
- [x] Save Image의 checklist / context-notes 이어 붙이기
- [x] 테스트(순서를 바꿔서도) + 패키지 로드 확인
- [x] GitHub `ComfyUI-Moon-Tools`에 push (사용자 확인 후)
- [ ] ComfyUI PC: 예전 `ComfyUI-Moon-SaveImage` 폴더 삭제 후 네 노드 동작 확인

## Plan 8 — 저장소 설명을 네 노드에 맞추기
- [ ] GitHub About 설명 변경 (사용자가 직접)
- [x] README 첫 문단에 네 노드 모두 소개
- [x] 문제 해결: 노드 검색은 `moon`으로 안내, 예전 폴더 충돌에 Save Image 추가
- [x] GitHub에 push (a28db61, raw 파일로 반영 확인)

## Plan 9 — Text List 표시 이름을 Moon Text List로
다른 세 노드처럼 `moon` 검색에 표시 이름으로 걸리게 한다. 노드 키 `TextList`는 그대로 둔다.
- [x] 표시 이름 `Text List` → `Moon Text List (TextList)` (`__init__.py`)
- [x] README의 노드 이름, 섹션 제목·링크, `moon` 검색 버전 안내 정리
- [x] 테스트 + 패키지 로드 확인
- [x] 커밋
- [x] push (ee993d7, GitHub 반영 확인)
- [ ] ComfyUI PC에서 `moon` 검색에 네 노드가 나오는지 확인

## Plan 10 — Any Index Switch index에 생성 후 제어
seed 위젯처럼 실행할 때마다 index를 fixed / increment / decrement / randomize로 바꾼다.
- [x] `index` 입력에 `control_after_generate: "fixed"` 추가 (`nodes/any_index_switch.py`)
- [x] 단위 테스트 (`tests/test_any_index_switch.py`)
- [x] README 반영
- [x] 커밋
- [x] push (4b81625, GitHub 반영 확인)
- [ ] ComfyUI PC에서 increment / randomize 동작 확인

## Plan 11 — 생성 후 제어를 연결된 입력 범위에서 순환
increment는 마지막 다음 0, decrement는 0 다음 마지막, randomize는 0 ~ 개수-1. index가 링크로 연결되면 동작하지 않는다.
- [x] 제어 위젯 훅을 감싸 범위를 잠시 넓히고 넘친 값을 반대쪽 끝으로 (`web/any_index_switch.js`)
- [x] 프론트엔드 제어 로직을 옮긴 Node 하네스로 확인 (고치기 전 JS는 실패)
- [x] README, context-notes 반영
- [x] 커밋
- [x] push (4b81625, GitHub 반영 확인)
- [ ] ComfyUI PC에서 increment / decrement / randomize 순환 확인

## Text List (ComfyUI-Moon-Text-List에서 통합)
통합 전 저장소의 기록이다(마지막 커밋 1d8775a). 파일 이름은 통합 전 기준이다.

### Plan
여러 줄 문자열을 리스트로 관리하고, index에 해당하는 문자열 하나를 출력하는 ComfyUI 커스텀 노드.
- 입력: text(여러 줄, 한 줄 = 항목 하나), index(INT, 0부터)
- 출력: STRING(index에 해당하는 항목)

### Tasks
- [x] 프로젝트 폴더 생성
- [x] 노드 구현 (`nodes.py`)
- [x] ComfyUI 등록 (`__init__.py`)
- [x] 단위 테스트 작성 및 통과 (`tests/test_nodes.py`)
- [x] git 초기화 및 커밋
- [ ] ComfyUI `custom_nodes`에 연결해 실제 동작 확인

### Plan 2 — 항목별 입력칸 UI
여러 줄 입력창 대신 항목마다 입력칸을 두고, 추가/삭제 버튼으로 관리한다.
- [x] `text` 입력 타입을 커스텀 타입 `TEXT_LIST`로 변경 (`nodes.py`)
- [x] 항목별 입력칸 + 추가/삭제 위젯 구현 (`web/text_list.js`)
- [x] `WEB_DIRECTORY` 등록 (`__init__.py`)
- [x] 단위 테스트 + JS 문법 검사
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 3 — 랜덤 On/Off
- [x] `random` BOOLEAN 입력 추가, On이면 index 대신 무작위 항목 출력
- [x] On일 때 `IS_CHANGED`로 매 실행마다 다시 뽑기
- [x] 단위 테스트
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 4 — index 범위 제한
- [x] random은 항목 수 범위 안에서만 뽑는지 확인 (기존 동작 유지)
- [x] index 위젯 최대값을 비어 있지 않은 항목 수 - 1로 맞추고, 범위를 벗어난 값은 최대값으로 당김
- [ ] ComfyUI PC에서 화살표 동작 확인

### Plan 5 — 보기/편집 전환 + 항목 내 줄바꿈
- [x] 항목은 평소 텍스트로 보여주고, 클릭하면 여러 줄 입력창으로 전환, 바깥 클릭 시 복귀
- [x] 저장 형식을 JSON 배열 문자열로 변경 (예전 줄 단위 형식도 읽음)
- [x] Python `parse_items` JSON 지원 + 테스트
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 6 — 항목 제목
항목마다 내용 위에 1줄 제목을 둔다. 보기 모드에서는 label, 클릭하면 제목/내용을 함께 편집한다.
- [x] 저장 형식을 `{title, text}` 객체 배열로 변경 (예전 문자열 항목도 읽음)
- [x] Python은 내용만 출력 (`item_text`) + 테스트
- [x] 보기 모드 제목 label / 편집 모드 제목 입력창을 내용 바로 위에 배치
- [x] 제목·내용 어느 쪽을 클릭해도 둘 다 편집 가능, 둘 사이 이동 시 편집 유지
- [x] jsdom으로 전환 동작 확인
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 7 — 제목 숨김
- [x] `show_title` BOOLEAN 입력 추가 (기본 On, 출력에는 영향 없음) + 테스트
- [x] Off면 보기/편집 모드 모두 제목을 숨기고, 새 항목은 내용 입력창부터 포커스
- [x] 토글 변경과 워크플로 불러오기 시 다시 그리기, jsdom으로 확인
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 8 — title 출력
- [x] 출력 슬롯 `title` 추가 (text 뒤, 기존 링크 유지)
- [x] 제목이 없으면 빈 문자열, `show_title` Off여도 출력
- [x] random일 때 같은 항목의 제목이 나가는지 테스트
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 9 — text_list 출력
- [x] 출력 슬롯 `text_list` 추가 (title 뒤, `OUTPUT_IS_LIST`로 STRING 리스트)
- [x] 빈 항목 제외, 빈 목록이면 빈 리스트 + 테스트
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 10 — title_list 출력
- [x] 출력 슬롯 `title_list` 추가 (text_list 뒤, 같은 항목·같은 순서)
- [x] 제목 없는 항목은 빈 문자열 + 테스트
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 11 — 출력 슬롯 순서 변경
- [x] 출력 순서를 `title, text, title_list, text_list`로 변경 + 테스트/README 반영
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 12 — 보기 모드 줄 수 자동 확장
- [x] 목록이 스크롤 없이 다 보이면 보기 모드 줄 수를 2줄에서 최대 5줄까지 늘림
- [x] 다시 그릴 때와 노드 크기가 바뀔 때 다시 맞춤, 편집 중에는 유지
- [x] 헤드리스 Chrome으로 높이별 줄 수 확인 + README 반영
- [x] 최대 5줄 제한 제거: 노드 높이에 맞춰 줄 수를 계속 늘림 (이진 탐색)
- [ ] ComfyUI PC에서 실제 동작 확인

### Plan 13 — 노드 검색 별칭
- [x] `SEARCH_ALIASES`에 `moon`, `text`, `textlist`, `text list` 추가 + 테스트/README 반영
- [ ] ComfyUI PC 노드 검색창에서 `moon`으로 찾히는지 확인

### Plan 14 — GitHub 공개용 README + 라이선스
다른 사람이 GitHub에서 받아 설치·사용할 수 있게 문서를 정리한다. 인기 커스텀 노드 README 구성과 라이선스를 참고한다.
- [x] ComfyUI·인기 노드 라이선스, Registry 라이선스 규정, README 구성 조사
- [x] 라이선스 결정: MIT (사용자 선택)
- [x] `LICENSE` 추가
- [x] `README.md` 영어로 재작성 (설치, 업데이트, 사용법, 입출력, UI 문구, 라이선스)
- [x] `README.ko.md` 한국어판 작성, 두 파일 서로 링크
- [x] 마크다운 링크 확인
- [x] 동작하지 않는 `control after generate` 팁 삭제
- [x] GitHub에 push (사용자 확인 후)

### Plan 15 — 저장소 이름 변경 (ComfyUI-Text-List → ComfyUI-Moon-Text-List)
- [x] README.md / README.ko.md 제목, clone 주소, 설치 폴더 경로 변경
- [x] 프론트엔드 확장 이름 `ComfyUI-Moon-Text-List.TextList`로 변경
- [x] 로컬 git remote 주소 변경
- [x] 테스트 + JS 문법 검사
- [x] GitHub 저장소 이름 변경 (사용자가 Settings에서 직접)
- [x] push 후 새 주소로 clone 되는지 확인 (GitHub 라이선스 MIT 인식, 옛 주소 301 연결)

## Moon Save Image (ComfyUI-Moon-SaveImage에서 통합)
통합 전 저장소의 기록이다(마지막 커밋 596bb94). 파일 이름은 통합 전 기준이다.

### Plan
입력 IMAGE를 파일로 저장하는 ComfyUI 커스텀 노드. 기본 `SaveImage` 노드를 바탕으로 WAS `Image Save` 등의 자주 쓰는 옵션을 더한다.
- 입력: images(IMAGE), filename_prefix(STRING, `%date:yyyy-MM-dd%`·`%width%`·`%height%` 치환), output_path(STRING, 비우면 output 폴더, 상대 경로는 output 기준, 절대 경로 허용), file_format(png/jpg/webp), quality(1~100, jpg·webp), save_metadata(On/Off)
- 출력: images(IMAGE, 입력 그대로 통과) + 노드 안 미리보기

### Tasks
- [x] 프로젝트 폴더 생성, git 초기화
- [x] 저장 로직 구현 (`nodes.py`)
- [x] ComfyUI 등록 (`__init__.py`)
- [x] 단위 테스트 작성 및 통과 (`tests/test_nodes.py`)
- [x] VS Code 설정 (`.vscode/settings.json`, unittest 탐색)
- [x] README, LICENSE 작성
- [x] 커밋
- [x] GitHub 저장소 생성 및 push
- [ ] ComfyUI PC에서 실제 동작 확인 (png/jpg/webp 저장, 워크플로 드래그 복원, 절대 경로 미리보기)

### Plan 2 — GitHub 공개 준비
- [x] README 공개용으로 정리: 영어 `README.md` + 한국어 `README.ko.md` (Text-List 구성)
- [x] LICENSE(MIT, javamoon71) 확인
- [ ] 저장소 공개 후 README 스크린샷 추가 (ComfyUI에서 노드 화면 캡처)

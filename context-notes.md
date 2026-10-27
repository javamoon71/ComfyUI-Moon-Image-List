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

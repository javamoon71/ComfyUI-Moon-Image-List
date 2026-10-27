# ComfyUI Moon Image List

여러 장의 이미지를 목록으로 관리하고, index 또는 랜덤으로 하나를 골라 출력하는 ComfyUI 커스텀 노드입니다. Load Image 노드를 여러 개 두는 대신 노드 하나로 이미지를 바꿔 가며 쓸 수 있습니다.

[ComfyUI-Text-List](https://github.com/javamoon71/ComfyUI-Text-List)의 이미지 버전입니다.

## 기능

- **이미지 추가**: `+ 이미지 추가` 버튼으로 고르거나, 이미지 파일을 노드 위에 끌어다 놓아(drag and drop) 여러 장을 한 번에 업로드합니다. 파일은 ComfyUI의 `input` 폴더에 저장됩니다.
- **썸네일 목록**: 항목마다 번호, 썸네일, 파일 이름, 삭제 버튼이 보입니다. 항목이 많으면 노드 안에서 스크롤합니다.
- **index 선택**: index 위젯은 이미지 수 범위 안에서만 움직입니다. 다른 노드에서 링크로 받은 index가 범위를 넘으면 이미지 수로 나눈 나머지를 씁니다(순환).
- **랜덤 선택**: `random`을 On으로 두면 index를 무시하고 실행할 때마다 이미지 하나를 무작위로 고릅니다.
- **출력 형식**: 기본 Load Image 노드와 같이 IMAGE와 MASK를 출력합니다. 알파 채널이 있으면 마스크로 씁니다.

## 설치

ComfyUI의 `custom_nodes` 폴더에 저장소를 복제한 뒤 ComfyUI를 다시 시작합니다.

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/javamoon71/ComfyUI-Moon-Image-List.git
```

추가로 설치할 Python 패키지는 없습니다.

## 사용법

노드 추가 메뉴에서 `moon`, `image`, `imagelist` 중 하나를 검색해 **Moon Image List (ImageList)** 노드를 추가합니다. 기존 워크플로와의 호환성을 위해 내부 노드 ID는 `ImageList`로 유지됩니다.

| 입력 | 타입 | 설명 |
| --- | --- | --- |
| `images` | IMAGE_LIST | 이미지 목록 (노드 안의 목록 UI로 관리) |
| `index` | INT | 출력할 이미지 번호 (0부터 시작) |
| `random` | BOOLEAN | On이면 index 대신 무작위로 선택 |

| 출력 | 타입 | 설명 |
| --- | --- | --- |
| `image` | IMAGE | 선택된 이미지 |
| `mask` | MASK | 선택된 이미지의 알파 마스크 (알파가 없으면 빈 마스크) |

**팁**: index 위젯의 `control after generate`를 `increment`로 두면 큐를 실행할 때마다 다음 이미지로 넘어갑니다.

목록이 비어 있거나 파일이 `input` 폴더에 없으면 실행할 때 에러가 납니다.

## 테스트

```bash
python -m unittest discover tests
```

## 구조

```
__init__.py         노드 등록
nodes.py            이미지 선택과 로드 로직
web/image_list.js   썸네일 목록과 업로드 UI (프론트엔드 확장)
tests/              단위 테스트
```

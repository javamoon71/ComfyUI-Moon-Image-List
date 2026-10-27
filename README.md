# ComfyUI Moon Image List

여러 이미지를 한 노드에서 관리하고, 인덱스 또는 무작위로 선택한 이미지를 출력하는 ComfyUI 커스텀 노드입니다. 이미지마다 `Load Image` 노드를 추가하지 않아도 됩니다.

## 주요 기능

- **여러 이미지 관리**: 파일 선택 또는 노드에 드래그 앤 드롭해 이미지를 추가하고, 목록에서 개별 항목을 삭제할 수 있습니다.
- **썸네일 미리보기**: 이미지 번호와 썸네일, 파일 이름을 노드 안에서 확인할 수 있습니다.
- **인덱스 선택**: 0부터 시작하는 인덱스로 이미지를 선택합니다. 범위를 벗어난 인덱스는 목록 길이에 맞춰 순환합니다.
- **무작위 선택**: `random`을 켜면 실행할 때마다 목록에서 이미지를 무작위로 선택합니다.
- **IMAGE와 MASK 출력**: 선택된 이미지를 `IMAGE`로, 알파 채널을 `MASK`로 출력합니다.

## 설치

ComfyUI를 종료한 뒤 저장소를 `custom_nodes` 폴더에 복제하고 ComfyUI를 다시 시작하세요.

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/javamoon71/ComfyUI-Moon-Image-List.git
```

추가 Python 패키지는 필요하지 않습니다.

## 사용법

1. ComfyUI에서 노드 검색을 열고 `moon`, `image` 또는 `imagelist`를 검색합니다.
2. **Moon Image List (ImageList)** 노드를 추가합니다.
3. **+ 이미지 추가**를 눌러 파일을 선택하거나 이미지 파일을 노드 위에 끌어다 놓습니다.
4. `index`로 출력할 이미지를 선택하거나 `random`을 켭니다.
5. `image` 또는 `mask` 출력을 원하는 노드에 연결합니다.

업로드한 이미지는 ComfyUI의 `input` 폴더에 저장됩니다. 노드의 이미지 목록은 워크플로에 저장됩니다.

## 입력 및 출력

| 구분 | 이름 | 타입 | 설명 |
| --- | --- | --- | --- |
| 입력 | `images` | `IMAGE_LIST` | 노드 UI에서 관리하는 이미지 목록 |
| 입력 | `index` | `INT` | 출력할 이미지의 0부터 시작하는 인덱스 |
| 입력 | `random` | `BOOLEAN` | 켜면 인덱스 대신 무작위로 이미지 선택 |
| 출력 | `image` | `IMAGE` | 선택한 이미지 |
| 출력 | `mask` | `MASK` | 알파 채널 마스크. 알파 채널이 없는 이미지는 빈 마스크를 출력 |

**팁:** `index` 위젯의 `control after generate`를 `increment`로 설정하면 큐를 실행할 때마다 다음 이미지로 이동할 수 있습니다.

## 문제 해결

- **노드를 찾을 수 없음:** 노드 검색에서 `moon`, `image`, `imagelist`를 검색하고, 설치 후 ComfyUI를 재시작했는지 확인하세요.
- **이미지 로드 오류:** 목록에 등록된 이미지 파일이 ComfyUI의 `input` 폴더에 있는지 확인하세요.
- **프론트엔드 UI가 갱신되지 않음:** ComfyUI를 재시작하고 브라우저를 새로고침하세요. 브라우저 캐시가 남아 있으면 강력 새로고침을 시도하세요.

## 개발 및 테스트

```bash
python -m unittest discover tests
```

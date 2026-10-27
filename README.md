# ComfyUI Moon Tools

ComfyUI 커스텀 노드 모음입니다. 이미지·텍스트 목록에서 인덱스나 무작위로 하나를 골라 출력하는 노드, 어떤 타입의 값이든 인덱스로 하나를 고르는 스위치, 형식·폴더·메타데이터를 고를 수 있는 이미지 저장 노드가 들어 있습니다.

| 노드 | 설명 |
| --- | --- |
| [Moon Image List](#moon-image-list) | 여러 이미지를 한 노드에서 관리하고, 인덱스 또는 무작위로 선택한 이미지를 출력 |
| [Moon Text List](#moon-text-list) | 여러 텍스트(프롬프트, 스타일, 캡션 등)를 목록으로 담아 두고, 인덱스 또는 무작위로 선택한 텍스트를 출력 |
| [Moon Any Index Switch](#moon-any-index-switch) | 어떤 타입의 값이든 여러 개 연결하고, 인덱스로 고른 값 하나를 출력 |
| [Moon Save Image](#moon-save-image) | 이미지를 PNG, JPG, WebP로 저장하고, 저장 폴더·품질·메타데이터 포함 여부를 선택 |

## 설치

ComfyUI를 종료한 뒤 저장소를 `custom_nodes` 폴더에 복제하고 ComfyUI를 다시 시작하세요.

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/javamoon71/ComfyUI-Moon-Tools.git
```

추가 Python 패키지는 필요하지 않습니다.

아직 ComfyUI-Manager 목록에는 없습니다. ComfyUI-Manager의 **Install via Git URL**에 위 저장소 주소를 넣어 설치할 수도 있습니다. 최근 ComfyUI-Manager는 Manager의 `config.ini`에 `allow_git_url_install = true`가 있어야 Git URL 설치를 허용합니다.

### 업데이트

```bash
cd ComfyUI/custom_nodes/ComfyUI-Moon-Tools
git pull
```

### 예전 저장소에서 옮겨 오기

이 저장소는 `ComfyUI-Moon-Image-List`에서 이름이 바뀌었고, `ComfyUI-Moon-Text-List`의 Text List 노드와 `ComfyUI-Moon-SaveImage`의 Moon Save Image 노드를 합쳤습니다. 노드 키는 그대로라 저장된 워크플로는 그대로 열립니다. Text List는 표시 이름만 **Moon Text List (TextList)**로 바뀌었습니다.

- **`ComfyUI-Moon-Image-List`를 설치했다면:** 그 폴더에서 `git pull`을 실행하세요. 옛 주소는 새 주소로 자동 연결됩니다.
- **`ComfyUI-Moon-Text-List`를 설치했다면:** 이 저장소를 설치한 뒤 `ComfyUI-Moon-Text-List` 폴더를 지우세요. 두 폴더가 함께 있으면 Moon Text List 노드가 두 번 등록되어 서로 덮어씁니다.
- **`ComfyUI-Moon-SaveImage`를 설치했다면:** 이 저장소를 설치한 뒤 `ComfyUI-Moon-SaveImage` 폴더를 지우세요. 두 폴더가 함께 있으면 Moon Save Image 노드가 두 번 등록되어 서로 덮어씁니다.

## Moon Image List

여러 이미지를 한 노드에서 관리하고, 인덱스 또는 무작위로 선택한 이미지를 출력합니다. 이미지마다 `Load Image` 노드를 추가하지 않아도 됩니다.

### 주요 기능

- **여러 이미지 관리**: 파일 선택 또는 노드에 드래그 앤 드롭해 이미지를 추가하고, 목록에서 개별 항목을 삭제하거나 드래그해 순서를 바꿀 수 있습니다.
- **썸네일 미리보기**: 이미지 번호와 썸네일, 파일 이름을 노드 안에서 확인할 수 있습니다.
- **인덱스 선택**: 0부터 시작하는 인덱스로 이미지를 선택합니다. 범위를 벗어난 인덱스는 목록 길이에 맞춰 순환합니다.
- **무작위 선택**: `random`을 켜면 실행할 때마다 목록에서 이미지를 무작위로 선택합니다.
- **IMAGE와 MASK 출력**: 선택된 이미지를 `IMAGE`로, 알파 채널을 `MASK`로 출력합니다.

### 사용법

1. ComfyUI에서 노드 검색을 열고 `moon`, `image` 또는 `imagelist`를 검색합니다.
2. **Moon Image List (ImageList)** 노드를 추가합니다.
3. **+ 이미지 추가**를 눌러 파일을 선택하거나 이미지 파일을 노드 위에 끌어다 놓습니다.
4. 목록의 이미지를 마우스로 끌어 원하는 위치에 놓으면 순서를 변경할 수 있습니다.
5. `index`로 출력할 이미지를 선택하거나 `random`을 켭니다.
6. `image` 또는 `mask` 출력을 원하는 노드에 연결합니다.

업로드한 이미지는 ComfyUI의 `input` 폴더에 저장됩니다. 노드의 이미지 목록은 워크플로에 저장됩니다.

### 입력 및 출력

| 구분 | 이름 | 타입 | 설명 |
| --- | --- | --- | --- |
| 입력 | `images` | `IMAGE_LIST` | 노드 UI에서 관리하는 이미지 목록 |
| 입력 | `index` | `INT` | 출력할 이미지의 0부터 시작하는 인덱스 |
| 입력 | `random` | `BOOLEAN` | 켜면 인덱스 대신 무작위로 이미지 선택 |
| 출력 | `image` | `IMAGE` | 선택한 이미지 |
| 출력 | `mask` | `MASK` | 알파 채널 마스크. 알파 채널이 없는 이미지는 빈 마스크를 출력 |

**팁:** `index` 위젯의 `control after generate`를 `increment`로 설정하면 큐를 실행할 때마다 다음 이미지로 이동할 수 있습니다.

## Moon Text List

여러 개의 텍스트(프롬프트, 스타일, 캡션 등)를 노드 하나에 목록으로 담아 두고, index나 랜덤으로 하나를 골라 출력합니다. 항목마다 짧은 제목을 붙일 수 있고, 전체 목록도 리스트로 출력합니다.

### 기능

- **노드 안에서 항목 편집**: 항목마다 한 줄 제목과 여러 줄 내용이 있습니다. 항목을 클릭하면 편집하고, 바깥을 클릭하면 끝납니다.
- **index 또는 랜덤 선택**: `index`로 항목을 고릅니다(0부터 시작). `random`을 On으로 두면 실행할 때마다 무작위로 고릅니다.
- **제목**: 선택된 항목의 제목은 `title`로 출력됩니다. `show_title`을 Off로 두면 목록에서 제목을 숨기고, `title` 출력은 그대로 나갑니다.
- **리스트 출력**: `title_list`와 `text_list`는 모든 항목을 같은 순서로 출력합니다. 여기에 연결된 노드는 항목마다 한 번씩 실행됩니다.
- **노드 크기에 맞춤**: 노드 크기는 정한 대로 유지됩니다. 항목이 많으면 목록이 스크롤되고, 노드를 키우면 항목마다 더 많은 줄이 보입니다.

### 사용법

노드 추가 메뉴의 **utils/text → Moon Text List (TextList)**에서 추가하거나, 캔버스를 더블클릭해 `moon`, `text list`, `textlist`, `text` 중 하나로 검색합니다.

1. **+ 항목 추가**를 눌러 제목과 내용을 입력합니다.
2. `index`로 원하는 항목을 고르거나 `random`을 On으로 둡니다.
3. `text`(필요하면 `title`도)를 다음 노드에 연결합니다. 예를 들어 CLIP Text Encode의 text 입력에 연결합니다.

### 입력

| 입력 | 타입 | 설명 |
| --- | --- | --- |
| `text` | TEXT_LIST | 노드 안에서 편집하는 항목 목록 |
| `index` | INT | 출력할 항목 번호 (0부터 시작) |
| `random` | BOOLEAN | On이면 `index`를 무시하고 실행할 때마다 무작위로 선택 |
| `show_title` | BOOLEAN | Off면 목록에서 제목을 숨김. 출력은 바뀌지 않음 |

### 출력

| 출력 | 타입 | 설명 |
| --- | --- | --- |
| `title` | STRING | 선택된 항목의 제목 (없으면 빈 문자열) |
| `text` | STRING | 선택된 항목의 내용 |
| `title_list` | STRING (리스트) | 모든 항목의 제목. `text_list`와 순서가 같음 (제목이 없으면 빈 문자열) |
| `text_list` | STRING (리스트) | 모든 항목의 내용. 연결된 노드는 항목마다 한 번씩 실행됨 |

### 세부 동작

- 내용이 빈 항목은 건너뜁니다. 번호 대신 `-`로 표시되고 출력에 들어가지 않습니다.
- 목록이 비어 있으면 `title`, `text`는 빈 문자열이고 리스트 출력은 빈 리스트입니다.
- `index` 위젯은 마지막 항목에서 멈춥니다. 다른 노드에서 링크로 받은 `index`가 범위를 넘으면 항목 수로 나눈 나머지를 씁니다(순환).
- 항목은 2줄까지 보이고 나머지는 `…`로 줄입니다. 노드를 키우면 더 많은 줄이 보이고, 충분히 크면 전체 내용이 보입니다.
- 편집 입력창은 10줄까지 커지고, 넘치면 스크롤됩니다. 제목 입력창에서 Enter를 누르면 내용 입력창으로 넘어갑니다.

## Moon Any Index Switch

`IMAGE`, `MODEL`, `STRING` 등 어떤 타입의 값이든 여러 개 연결하고, `index`로 고른 값 하나를 출력합니다.

- **입력 자동 추가**: 처음에는 `value0`만 있고, 마지막 입력을 연결하면 다음 입력이 생깁니다. 끝의 연결을 끊으면 남는 빈 입력이 정리됩니다.
- **인덱스 순환**: 연결된 입력을 위에서부터 0, 1, 2…로 셉니다. 중간에 빈 입력은 건너뛰고, 범위를 벗어난 인덱스는 연결된 입력 개수에 맞춰 순환합니다.
- **선택된 입력만 실행**: 고른 입력에 연결된 노드만 실행하고, 나머지 입력 쪽 노드는 실행하지 않습니다.

노드 검색에서 `moon`, `switch` 또는 `anyindexswitch`를 검색해 **Moon Any Index Switch (AnyIndexSwitch)** 노드를 추가하세요.

| 구분 | 이름 | 타입 | 설명 |
| --- | --- | --- | --- |
| 입력 | `index` | `INT` | 출력할 입력의 0부터 시작하는 인덱스 |
| 입력 | `value0`, `value1`, … | 모든 타입 | 고를 값들. 연결하면 다음 입력이 추가됨 |
| 출력 | `value` | 모든 타입 | 선택한 입력의 값 |

## Moon Save Image

이미지를 PNG, JPG, WebP 파일로 저장합니다. 기본 **Save Image** 노드처럼 쓰면서 저장 폴더, 파일 형식, 품질을 고르고, 메타데이터 포함 여부를 정할 수 있습니다. 이미지 출력이 있어서 다음 노드로 이어서 연결할 수도 있습니다.

### 기능

- **파일 형식**: PNG, JPG, WebP 중 하나로 저장합니다. JPG와 WebP는 `quality`로 품질을 정합니다.
- **저장 폴더**: `output_path`를 비워 두면 ComfyUI `output` 폴더에 저장합니다. 상대 경로는 `output` 아래에, 절대 경로는 그 위치에 저장하고, 없는 폴더는 만듭니다.
- **파일 이름 토큰**: `filename_prefix`와 `output_path`에 `%date:yyyy-MM-dd%`, `%width%`, `%height%`를 쓸 수 있습니다.
- **메타데이터 On/Off**: `save_metadata`를 켜면 프롬프트와 워크플로를 파일에 넣습니다. 저장한 PNG나 WebP를 ComfyUI에 끌어다 놓으면 워크플로가 다시 열립니다.
- **미리보기**: 저장한 이미지를 노드 안에서 보여 줍니다. `output` 폴더 밖에 저장해도 보입니다.
- **이미지 통과 출력**: `images` 출력은 입력 이미지를 그대로 내보내므로 워크플로 중간에 둘 수 있습니다.
- **덮어쓰기 없음**: 기본 노드처럼 번호를 붙이고(`ComfyUI_00001_.png`), 폴더에 있는 가장 큰 번호 다음부터 이어 갑니다.

### 사용법

노드 추가 메뉴의 **image → Moon Save Image (MoonSaveImage)**에서 추가하거나, 캔버스를 더블클릭하고 `moon save image`를 검색합니다.

1. `images`에 이미지를 연결합니다.
2. `filename_prefix`, `output_path`, `file_format`, `quality`를 정합니다.
3. 워크플로를 실행합니다. 저장한 이미지가 노드에 나타납니다.

예를 들어 `output_path`를 `%date:yyyy-MM-dd%`로, `filename_prefix`를 `portrait`로 두면 `output/2026-10-27/portrait_00001_.png`에 저장됩니다.

### 입력

| 입력 | 타입 | 설명 |
| --- | --- | --- |
| `images` | IMAGE | 저장할 이미지. 배치면 모두 저장 |
| `filename_prefix` | STRING | 파일 이름 앞부분. `portraits/test`처럼 폴더 포함 가능 |
| `output_path` | STRING | 저장 폴더. 비우면 `output`, 상대 경로는 `output` 아래, 절대 경로는 그대로 |
| `file_format` | `png` / `jpg` / `webp` | 파일 형식 |
| `quality` | INT | JPG, WebP 품질 1~100 (기본 95). PNG에는 적용되지 않음 |
| `save_metadata` | BOOLEAN | On이면 프롬프트와 워크플로를 파일에 넣음 |

### 출력

| 출력 | 타입 | 설명 |
| --- | --- | --- |
| `images` | IMAGE | 입력 이미지를 그대로 출력 |

### 파일 이름 토큰

| 토큰 | 예 | 결과 |
| --- | --- | --- |
| `%date:형식%` | `%date:yyyy-MM-dd%` | `2026-10-27` |
| `%width%`, `%height%` | `%width%x%height%` | `1024x768` |

날짜 형식에는 기본 Save Image 노드와 같은 `yyyy`, `yy`, `MM`, `M`, `dd`, `d`, `hh`, `h`, `mm`, `m`, `ss`, `s`를 씁니다. `hh`는 24시간제입니다. 그 밖의 `%...%`는 바꾸지 않고 그대로 둡니다.

### 형식별 메타데이터

| 형식 | 저장 위치 | 비고 |
| --- | --- | --- |
| PNG | 텍스트 청크(`prompt`, `workflow`) | 기본 Save Image와 같음 |
| WebP | EXIF | 기본 SaveAnimatedWEBP와 같음 |
| JPG | 저장하지 않음 | JPEG EXIF는 64KB 제한이 있어 대부분의 워크플로를 담을 수 없음 |

### 세부 동작

- 파일 이름은 `{filename_prefix}_{번호}_.{확장자}`이고 번호는 5자리입니다. 같은 폴더에서는 형식이 달라도 번호가 이어집니다.
- JPG는 투명도를 지원하지 않으므로 알파 채널이 있는 이미지는 RGB로 저장합니다.
- WebP는 quality가 100이어도 손실 압축으로 저장합니다.
- ComfyUI 실행 옵션 `--disable-metadata`는 이 노드에 적용되지 않습니다. 대신 `save_metadata`를 쓰세요.
- `output` 밖에 저장한 이미지는 미리보기용 사본이 ComfyUI `temp` 폴더에 저장됩니다. `temp` 폴더는 ComfyUI를 시작할 때 비워집니다.

## 보안

기본 Save Image 노드는 `output` 폴더 밖에 저장하지 못하게 막습니다. Moon Save Image는 절대 경로와 `..`을 허용하므로, ComfyUI 서버에서 워크플로를 실행할 수 있는 사람은 ComfyUI 프로세스가 쓸 수 있는 모든 위치에 이미지 파일을 저장할 수 있습니다. 여러 사람이 쓰는 서버에 이 팩을 설치할 때는 이 점을 고려하세요.

## 문제 해결

- **노드를 찾을 수 없음:** 노드 검색에서 `moon`을 검색하면 네 노드가 모두 나옵니다. 설치 후 ComfyUI를 재시작했는지 확인하세요.
- **이미지 로드 오류:** 목록에 등록된 이미지 파일이 ComfyUI의 `input` 폴더에 있는지 확인하세요.
- **프론트엔드 UI가 갱신되지 않음:** ComfyUI를 재시작하고 브라우저를 새로고침하세요. 브라우저 캐시가 남아 있으면 강력 새로고침을 시도하세요.
- **Moon Text List나 Moon Save Image가 이상하게 동작함:** `custom_nodes`에 예전 `ComfyUI-Moon-Text-List`나 `ComfyUI-Moon-SaveImage` 폴더가 남아 있는지 확인하세요. [예전 저장소에서 옮겨 오기](#예전-저장소에서-옮겨-오기)를 참고하세요.
- **저장한 이미지에서 워크플로가 열리지 않음:** Moon Save Image의 `save_metadata`가 켜져 있는지, 형식이 PNG나 WebP인지 확인하세요.

## 개발 및 테스트

테스트에는 ComfyUI가 이미 설치하는 `torch`, `numpy`, `Pillow`가 필요합니다.

```bash
python -m unittest discover tests
```

```
__init__.py   노드 등록
nodes/        노드 로직 (노드마다 파일 하나)
web/          프론트엔드 확장 (목록 UI, 입력 슬롯 자동 추가)
tests/        단위 테스트 (노드마다 파일 하나)
```

## 라이선스

이 프로젝트는 [MIT License](./LICENSE)에 따라 배포됩니다.

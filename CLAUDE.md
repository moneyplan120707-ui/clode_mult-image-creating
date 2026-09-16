# 금광롱폼 × 클로드코드

유튜브 롱폼 영상 제작 파이프라인. **TTS 음성이 들어간 Vrew 프로젝트(.vrew, v16)** 를 넣으면
클립 추출 → Claude 스토리보드 → 이미지 생성 → Vrew 에 이미지 연결까지 자동으로 돌아간다.
사용자는 클로드코드에서 대화로 실행한다. 스킬: `/longform-pipeline` (`.claude/skills/longform-pipeline/SKILL.md`).

## 폴더 구성

```
Vrew_Auto_Pipeline_V1_0.py   ← 진입점. 오케스트레이터 (login → extract → storyboard → characters → images → connect)
                               login 단계가 맨 앞에서 Google Flow 로그인을 끝내므로, 그 뒤로는 자리를 비워도 된다
setup_runtime.py             ← runtime/ 설치기 (독립 파이썬 3.11 + requirements.txt + Chromium). 시스템 파이썬은 건드리지 않는다
requirements.txt             ← 모든 도구가 쓰는 패키지 목록
runtime/                     ← 설치 결과: python/ (또는 venv/), ms-playwright/. 파이프라인이 자동으로 이 파이썬으로 재실행된다
tools/                       ← 도구 스크립트. 서로 import 하므로 반드시 한 폴더에 둔다 (깃에는 파이프라인이 쓰는 6개만 올린다 — .gitignore)
prompts/                     ← 스토리보드 프롬프트 마법사 txt (Claude 규칙 문서, 최신 버전 1개만 유지)
characters/                  ← 캐릭터 참조 이미지 <영문이름>.png (이멀플이 이름으로 자동 첨부)
projects/                    ← 브루 프로젝트별 폴더 <YYYYMMDD>_<브루파일명>/ (init 이 만든다; 사용자 확인 후 생성)
packaging/                   ← PyInstaller .spec / .ico (exe 배포용, 평소엔 안 씀 · 로컬 전용, 깃 제외)
tools/ui_static/             ← 금광 스튜디오(UI) 정적 파일 index.html / studio.css / studio.js
studio_defaults.json         ← (UI 가 만듦) 새 프로젝트의 기본 설정. 프로젝트별 설정은 projects/<이름>/<이름>_settings.json
```

프로젝트 폴더 산출물: `<이름>_클립정보.xlsx` → `<이름>_스토리보드.xlsx` (+ `_스토리보드_분석.json`) → `Image/` → `<이름>_이미지연결_<시각>.vrew`.
진행 상태는 `<이름>_pipeline.json`, 로그는 `<이름>_pipeline.log`.

## 실행

```bash
python setup_runtime.py                                                        # 최초 1회: runtime/ 설치 (--check 로 상태 확인)
python Vrew_Auto_Pipeline_V1_0.py init "<어디든>/<이름>.vrew"                   # projects/<오늘날짜>_<이름>/ 생성 + 복사 (사용자에게 먼저 물어본 뒤)
python Vrew_Auto_Pipeline_V1_0.py run "projects/<이름>/<이름>.vrew"            # 이미지만
python Vrew_Auto_Pipeline_V1_0.py status "projects/<이름>/<이름>.vrew"
python Vrew_Auto_Pipeline_V1_0.py login                                        # 이멀플(Google Flow) 로그인
python Vrew_Auto_Pipeline_V1_0.py run ... --only <extract|storyboard|characters|images|connect>
python Vrew_Auto_Pipeline_V1_0.py ui                                           # 금광 스튜디오 UI (127.0.0.1:7788, 이미 떠 있으면 탭만 엶)
python Vrew_Auto_Pipeline_V1_0.py status "projects/<이름>/<이름>.vrew" --json  # 스크립트/UI 용
```

- **금광 스튜디오(UI)** `tools/Studio_UI_V1_0.py` + `tools/ui_static/` — 사용자가 "UI 띄워" 라고 하면 `ui` 로 띄운다(의존성 0, 표준 http.server, 분리 프로세스라 세션이 끝나도 남는다; 끄라고 할 때만 끈다).
  **UI 는 파이프라인을 실행하지 않는다.** 탭 순서 = 작업 순서: 🔐 로그인(Flow 슬롯·환경, 처음에 먼저) → 🎞 프로젝트·설정(vrew 넣기·프로젝트 이름·마법사 단계 2~3·참조 방식·이미지 옵션·
  **검수 게이트**(storyboard/characters/images) → `<이름>_settings.json` 저장 → **클로드코드에 붙여 넣을 문장** 생성) → 📝 스토리보드(이미지별 카드, Image/ 2초 감시, 인물별 참조 이미지 프롬프트)
  → 👤 캐릭터(시트 확인·반려 삭제·업로드) → 🎬 생성 모니터(진행·반려 삭제) → 📦 결과([최종 Vrew 파일 만들기] = connect 단계만 UI 가 직접 실행, 열기·다운로드).
  UI 가 파이프라인을 실행하는 유일한 예외가 이 connect 버튼이다(몇 초짜리, Claude 불필요 — 2026-09-11 사용자 요청). 진행 판정은 `<이름>_pipeline.log` 의 STEP/실행 종료 표식으로 한다.
  `run` 은 `<이름>_settings.json` 을 자동으로 읽고(CLI 인자가 우선) 끝날 때 `─── 실행 종료 ───` 를 로그에 남긴다. 게이트에서 멈추고 이어가는 절차는 스킬 0-a 절.

- **켄번즈(줌·팬) 효과**는 connect 단계에서 Vrew_Connector 가 스토리보드 8열 값으로 넣는다(Claude 가 이미지마다 지정). `--kenburns random`(이미지마다 무작위, 마지막은 none) /
  `--kenburns none`(효과 없음)이면 `<이름>_스토리보드_연결용.xlsx` 를 따로 써서 연결한다(원본 스토리보드는 그대로). 스튜디오 설정 "Vrew 연결 · 켄번즈 효과"와 같다.
- 재실행하면 끝난 단계는 건너뛴다. 처음부터: `--force`.
- 종료 코드 **3** = `<이름>_스토리보드_요청.txt` 를 만들고 스토리보드를 기다리는 것(**기본 동작이며 오류가 아니다**). Claude 가 이미지 그룹 JSON 배열을 만들어 `<이름>_스토리보드.json` 으로 저장한 뒤 다시 run.
- 스토리보드 백엔드: **claude CLI(`claude -p`) 백엔드는 제거됨**(2026-09-12 사용자 요청 — 어떤 경우에도 CLI 를 부르지 않는다). auto = `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` 이 있으면 Anthropic API, 없으면 manual(종료 코드 3 → 이 세션이 작성).
  스토리보드만 한 번 채우면 characters → images → connect 는 그대로 무인으로 끝까지 돈다.
- 스토리보드 설정은 프롬프트 마법사 단계 2~3 의 질문 그대로 **스킬이 run 전에 사용자에게 순서대로 묻는다**(스타일 고정용 프롬프트 → 목표 장수/분할 방식 → 캐릭터 참조 이미지 방식)
  → `--style-prompt` / 영상 전체 N장 `--target-images N` 또는 초반 집중 `--split-mode front --front-minutes M --front-per-min A --front-rest-per-min B`
  (처음 M분은 분당 A장, 이후 분당 B장 = 라움튜브 front:M:A,rest:B, 기본 10/3/1; 균등 간격 `--split-mode uniform --block-seconds S` 는 요청 시만) / `--no-characters`. 마법사 단계 1 의 캐릭터 고유 묘사 블록은 묻지 않고 항상 쓴다. 파이프라인 자체는 질문하지 않고 확정값만 Claude 에 넘긴다.
  Claude 와의 교환 형식은 JSON 이다: 이미지(그룹)당 `{img, from_clip, to_clip, chars, prompt, kenburns}` 하나, 클립번호·시간·대본은 파이프라인이 원본에서 채운다
  (`rows_from_image_groups` → `validate_storyboard`). 엑셀(8열)은 다른 도구들이 읽는 공용 산출물이라 항상 만든다. 옛 `| 구분 CSV` 수동 파일도 아직 읽는다.
- 동영상은 파이프라인이 만들지 않고, 스튜디오 UI 의 동영상 넣기 기능도 뺐다(둘 다 2026-09-11 사용자 결정). Vrew_Connector 규칙(같은 번호에 `Image/<번호>_*.mp4` 가
  있으면 이미지 대신 동영상 연결)만 남아 있어, 파일을 직접 두고 `--only connect` 를 돌리면 반영된다.
- **이미지 백엔드 기본은 `emf`** (EasyMultyFlow_v5_6, flow.google.com batchexecute RPC). 프로젝트 하나를 만들어(`<이름>_flow_project.json` 에 id 저장, FlowUI 와 공유)
  그 안에 생성한다. 한 호출에 `--batch`(기본 3)장, 2장 ≈ 30초. `--headless` 로 창 없이 돌 수 있다 — 헤드리스 Chrome 의 UA(`HeadlessChrome`)를
  그대로 두면 Flow 가 `PUBLIC_ERROR_UNUSUAL_ACTIVITY`(403)로 거부하므로(2026-09-11 실측) 이멀플이 UA 를 `Chrome` 으로 교정해 다시 띄운다
  (참고 구현 `Desktop/scripts/flow_launch.py` 와 같은 방식). 그래도 그 사유의 403 이 오면 스스로 창 모드로 전환한다. 창이 떠 있어도 건드리지 않으면 무인.
- `--image-backend flowui` 는 화면 자동화 폴백(FlowUI_Gen_V1_0, 1장 ≈ 45초, 참조 첨부 불가 → characters 단계 생략). RPC 형식이 또 바뀌어 이멀플이 막히면 이걸 쓴다.
  Flow UI 가 바뀌면 `FlowUI_Gen_V1_0.py` 의 셀렉터(설정 트리거 / 생성 시작 / .ProseMirror / flow-content.google 이미지)를 손본다.
- **캐릭터 참조 이미지**는 (emf 백엔드일 때) `characters` 단계가 자동으로 만든다: 스토리보드 분석 JSON 의 인물 외형 묘사로 이멀플이 1인 1장 캐릭터 시트를 뽑아
  `projects/<이름>/characters/<이름>.jpg` 로 저장하고, images 단계가 이름으로 자동 첨부한다. 사용자가 직접 준비한 이미지가
  `characters/<이름>.png`(공용) 또는 `projects/<이름>/characters/`(프로젝트) 에 있으면 그 인물은 생성하지 않고 그것을 쓴다. 생략: `--no-characters`.

## 도구 (tools/)

| 스크립트 | 역할 | 파이프라인에서 쓰는 부분 |
|---|---|---|
| Vrew_Connector_V1_8 | Vrew ↔ 엑셀, 이미지/동영상 연결, v16 변환 | `extract_clips_from_vrew`, `add_images_to_vrew`, `detect_vrew_version` |
| Studio_UI_V1_0 | 금광 스튜디오 — 파이프라인 자동화 로컬 UI (http.server + ui_static/) | `ui` 서브커맨드가 띄움. 설정 저장·문장 생성·진행 표시만 하고 파이프라인은 실행하지 않음(실행은 클로드코드) |
| FlowUI_Gen_V1_0 | flow.google.com 화면 자동화 이미지 생성 (Playwright) — 이멀플 RPC 가 막혔을 때의 폴백 | `--image-backend flowui` 일 때 `--login`, `--generate/--only/--project-store` |
| **EasyMultyFlow_v5_6** | **Google Flow 이미지 배치 생성 — flow.google.com batchexecute RPC(ogiZ0b/maseQ) 직접 호출 (Playwright, PySide6 GUI 겸용). 참조 이미지 첨부·한 호출 N장** | `--login`, `--generate/--char-dir/--project-store` 서브프로세스 |
| Multi_Genspark_V3_3 | Genspark 이미지 배치 생성 (Selenium) | `--cli` 서브프로세스 (대체 백엔드) |
| GrokVideoGen_v2_0 | Grok Imagine 이미지→동영상 (Selenium, PySide6) | 파이프라인 미사용 (단독 GUI) |
| GrokAutoNumbering_V3_6 | 동영상↔이미지 첫 프레임 매칭 (OpenCV) | 파이프라인 미사용 (단독 GUI) |
| StoryBoard_Checker_V2_0 | AI 스토리보드 ↔ 원본 클립 검증 | `parse_excel`, `compare_clips` |
| Easy_CapCut_V3_5 / SRT_Tool_V1_2 / CSV_TO_EXCEL_V2_6 | 캡컷 프로젝트 생성 / SRT 보정 / CSV→엑셀 | 파이프라인 미사용 (단독 GUI) |
| Workflow_Agent_V5_5 | 위 도구들의 tkinter 허브 GUI (5단계 수동 워크플로우) | 파이프라인 미사용 |
| Multi_Flow_V10_2 | Google Flow Selenium 구버전 | 미사용 (이멀플로 대체) |

## 규약 (바꾸면 여러 도구가 같이 깨짐)

- **스토리보드 엑셀 8열 고정 순서**: 클립번호 | 시작시간 | 끝시간 | 대본 | 이미지 번호 | 등장인물 | 프롬프트 | 켄번즈. Vrew_Connector 는 열 위치(1~5, 8)로 읽는다.
- 동일 이미지 그룹: 이미지 번호는 모든 행, 등장인물/프롬프트/켄번즈는 그룹 첫 행에만. 마지막 클립 켄번즈는 `none`.
- 미디어 파일명은 `<이미지번호>_...` 로 시작. 같은 번호에 이미지·동영상이 있으면 동영상 우선, 같은 종류면 최신 파일.
- 등장인물 이름은 영문, 공백 대신 `_`. `characters/<이름>.png` 와 이름이 같아야 자동 첨부된다.
- Vrew 는 v16 만 지원. v14/15 는 Vrew 에서 [다른 이름으로 저장] 후 사용.
- 파일명 버전 접미사(`_V1_0`) 가 버전 관리다. 도구를 올리면 파일명을 바꾸고 `Workflow_Agent`/`packaging/*.spec`/이 파일의 참조도 같이 바꾼다.

## 환경

- **모든 실행은 `runtime/` 의 파이썬으로 한다.** `python setup_runtime.py` 가 python-build-standalone 3.11(tkinter 포함)을 `runtime/python/` 에 내려받고
  requirements.txt 와 Playwright Chromium(`runtime/ms-playwright/`)을 그 안에 설치한다. 파이프라인은 시작 시 runtime 파이썬으로 자동 재실행되고
  `PLAYWRIGHT_BROWSERS_PATH` 도 맞춰 준다. 시스템 파이썬(3.11, `C:\Users\J\AppData\Local\Programs\Python\Python311`)에는 pip install 하지 않는다.
- 도구를 단독(GUI)으로 돌릴 때도 runtime 파이썬을 쓴다: `runtime\python\python.exe tools\Workflow_Agent_V5_5.py`.
- 새 패키지가 필요하면 requirements.txt 에 추가하고 `python setup_runtime.py --upgrade`.
- 파이프라인은 `claude` CLI 를 부르지 않는다(2026-09-12 제거). 설치·실행 어디에도 CLI 는 필요 없다 — 스토리보드는 이 세션이 쓴다.
- 브라우저 로그인 상태(이멀플 `tools/browser_profile/`, `tools/accounts.json`)는 tools/ 아래에 쌓인다. 지우면 다시 로그인.

## 작업 시 주의

- 도구 스크립트는 사용자가 GUI 로도 쓰는 완성품이다. 파이프라인 때문에 고칠 일이 생기면 최소 수정 + 버전 접미사 올리기.
- 긴 실행(이미지 수백 장)은 백그라운드로 돌리고, `progress "<VREW>" --watch 30` 을 Monitor 로 걸어 **30초마다 진행 한 줄을 대화창에 옮겨 적는다**(사용자 지시 2026-09-12 — 조용히 기다리지 않는다).
- 브라우저 로그인(이멀플 Google Flow)은 사람이 직접 해야 한다. 그래서 `login` 단계가 run 시작 직후에 먼저 확인하고,
  없으면 창을 띄워 최대 5분 기다린다. 사용자 원칙: **로그인은 처음 한 번, 그 뒤는 무인.** 중간에 로그인을 요구하는 흐름을 만들지 않는다.
- EasyMultyFlow 는 v5.6 에서 flow.google.com 신 앱 규격으로 재구현됨(`Flow_이전_대응_보고_2026-09-11.md` 이식): 로그인 감지 = `WIZ_global_data.oPEP7c`,
  생성 = batchexecute `ogiZ0b`, 참조 업로드 = `maseQ`, 인증 = 쿠키 + XSRF `at`(`SNlM0e`). 옛 `/fx/api/auth/session`·aisandbox-pa REST 경로는 삭제.
  RPC 응답 파싱이 실패하면 `tools/_rpc_debug/` 에 원문이 남는다(`EMF_RPC_DEBUG=1` 이면 전부). 업스케일(2K/4K)은 새 rpcid 미확인이라 무시된다.
- 계정 한도(403/429 누적 → "한도 소진")가 뜨면 `--account <다른슬롯>` 으로 바꿔 재실행한다. 이미 만든 이미지는 건너뛴다.

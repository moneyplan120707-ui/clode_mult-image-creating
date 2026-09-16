# 금광롱폼 × 클로드코드 — 설치·사용 가이드

TTS 음성이 들어간 **Vrew 프로젝트(.vrew, v16)** 하나를 넣으면
**클립 추출 → Claude 스토리보드 → 캐릭터 시트 → 이미지 생성(Google Flow) → Vrew 에 이미지 연결**까지 자동으로 돌아가는 롱폼 제작 파이프라인입니다.
실행은 **클로드코드(Claude Code)** 세션이 하고, **금광 스튜디오(로컬 UI)** 에서 로그인·설정·검수 게이트를 정하고 진행 상황을 봅니다.

> **이용 조건** — 「금광롱폼 × 클로드코드」 수강생 본인의 학습·콘텐츠 제작용입니다. 만든 영상·이미지는 본인 채널에 자유롭게 쓰셔도 되지만, **저장소 파일 자체를 제3자에게 재배포·공유·판매하는 것은 금지**입니다. 전문은 [LICENSE](LICENSE).

---

## 내려받기 (처음 한 번)

Git 이 없으면 먼저 설치: https://git-scm.com/download/win (전부 [Next] 로 기본값 설치)

```powershell
cd $HOME\Desktop
git clone https://github.com/88raom-ai/goldmine-longform-claudecode.git 금광롱폼
cd 금광롱폼
```

## 업데이트 (수업 자료가 바뀌었을 때)

```powershell
cd $HOME\Desktop\금광롱폼
git pull
```

> `git pull` 이 **"Your local changes would be overwritten"** 이라고 막으면, 도구 파일을 직접 고친 것입니다.
> 내 수정본을 버리고 최신으로 맞추려면 `git checkout -- .` 뒤에 `git pull`,
> 남겨 두려면 `git stash` → `git pull` → `git stash pop`.
>
> **내 작업물은 `git pull` 로 지워지지 않습니다.** `projects\`(산출물) · `runtime\`(설치본) ·
> `characters\`(참조 이미지) · 로그인 정보는 저장소에 올라가지 않도록 빠져 있어서, 항상 내 PC 에만 남습니다.

---

## 설치 (Setup)

> **환경**: Windows 11 / PowerShell. Python 은 부트스트랩용으로만 아무 3.x 가 있으면 됩니다(설치 중 `Add python.exe to PATH` 체크).
> 실제 실행 환경(파이썬 3.11 + 라이브러리 + Chromium)은 이 폴더 안 `runtime\` 에 따로 설치되며 시스템 파이썬을 건드리지 않습니다.

### 1) 원샷 부트스트랩 (권장)

```powershell
cd <이 폴더>
.\setup.ps1              # runtime\ 설치(독립 파이썬 3.11 + requirements.txt + Chromium) + 점검, 5~10분
.\setup.ps1 -UI          # 설치 후 바로 금광 스튜디오 띄우기
```

옵션: `-Check`(상태만 확인) · `-NoBrowser`(Chromium 생략) · `-Upgrade`(라이브러리 최신) · `-Login`(끝에 Google Flow 로그인 창)

PowerShell 이 스크립트 실행을 막으면 한 번만:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 2) 수동 설치

```powershell
python setup_runtime.py            # runtime\python + requirements.txt + Chromium
python setup_runtime.py --check    # 상태 확인
```

### 3) 그게 전부입니다

**따로 설치할 것은 없습니다.** 클로드코드 CLI(`claude.exe`)도, API 키도 필요 없습니다 —
파이프라인은 스토리보드 차례가 되면 요청 파일(`<이름>_스토리보드_요청.txt`)을 만들고 종료 코드 3 으로 멈추고,
**클로드코드 대화창의 세션이 직접** 스토리보드 JSON 을 만들어 저장하면 그대로 이어집니다(정상 흐름).
그 뒤 캐릭터 시트 → 이미지 생성 → Vrew 연결은 사람 없이 끝까지 돕니다.

> (선택) `ANTHROPIC_API_KEY` 환경변수가 있으면 파이프라인이 Anthropic API 로 스토리보드까지 스스로 만듭니다. 없어도 됩니다.

### 알아둘 것

- **모든 실행은 `runtime\python\python.exe`** 로 합니다. `Vrew_Auto_Pipeline_V1_0.py` 는 시스템 파이썬으로 실행해도 runtime 파이썬으로 자동 재실행됩니다.
- **로그인은 사람이 합니다** — Google Flow(이멀플)는 스튜디오 🔐 로그인 탭에서 뜨는 Chrome 창에서 로그인(처음 한 번). 프로필은 `tools\browser_profile\` 에 저장됩니다.
- **다른 PC 로 옮기기** — 폴더 안 경로는 전부 상대 경로라 폴더째 복사하면 됩니다. 옮긴 PC 에서 `.\setup.ps1` 을 다시 돌려 `runtime\` 을 그 PC 에 맞게 설치하고, 스튜디오에서 다시 로그인하세요(브라우저 프로필은 PC 마다 다릅니다).
- Vrew 는 **v16** 만 지원합니다. v14/15 파일은 Vrew 에서 [다른 이름으로 저장] 후 쓰세요.

---

## 처음 한 번 돌려 보기

```powershell
.\runtime\python\python.exe Vrew_Auto_Pipeline_V1_0.py ui     # 금광 스튜디오 (http://127.0.0.1:7788)
```

1. **🔐 로그인** — Google Flow 계정 슬롯에서 [로그인 창 열기] → Chrome 창에서 Google 로그인 → "로그인됨".
   서버를 껐다 켜야 할 때(코드 수정 뒤 등)는 프로젝트 루트의 **`스튜디오_재시작.bat`** 을 더블클릭한다 — 7788 포트의 서버를 끄고 다시 띄운 뒤 브라우저 탭을 연다.
2. **🎞 프로젝트 · 설정** — .vrew 파일 선택 → 프로젝트 이름 → [만들기]. 설정(스타일 프롬프트 · 목표 장수/분할 · 캐릭터 참조 방식, 모델·배치, 창 모드)과 **검수 게이트**(스토리보드 / 캐릭터 시트 / 이미지)를 고르고 [저장].
3. **[📋 저장하고 복사]** → 만들어진 문장을 **클로드코드 대화창에 붙여 넣기**. 예:
   ```
   /longform-pipeline 프로젝트 "20260911_영상" 를 스튜디오 설정대로 돌려줘.
   - Vrew: projects/20260911_영상/영상.vrew
   - 설정은 영상_settings.json 에 저장돼 있어 … 요약 …
   - 검수 게이트: 스토리보드, 캐릭터 시트 — 그 단계가 끝나면 멈추고 알려줘. "계속" 이라고 하면 이어가고, "다시" 라고 하면 그 단계를 다시 만들어.
   ```
4. 클로드코드가 파이프라인을 돌립니다. 게이트에서 멈추면 스튜디오의 📝 스토리보드 / 👤 캐릭터 / 🎬 생성 모니터 탭에서 확인하고, 클로드코드에 **"계속"** 또는 **"다시"** 라고 답합니다.
5. **📦 결과** 탭에서 `<이름>_이미지연결_<시각>.vrew` 를 [Vrew 로 열기].


## 클로드코드에서 바로 쓰기 (UI 없이)

```
python Vrew_Auto_Pipeline_V1_0.py init "어디든/영상.vrew"                 projects/<오늘날짜>_영상/ 만들기
python Vrew_Auto_Pipeline_V1_0.py run  "projects/<이름>/영상.vrew"        전체 실행 (끝난 단계는 건너뜀)
python Vrew_Auto_Pipeline_V1_0.py run  ... --only storyboard --force     스토리보드만 다시
python Vrew_Auto_Pipeline_V1_0.py status "projects/<이름>/영상.vrew"      진행 상태
```
클로드코드에서 "브루 파일 넣었어, 이미지 만들어 줘" 라고 해도 `/longform-pipeline` 스킬이 같은 질문(설정 3개 + 참조 방식)을 하고 돌립니다.

---

## 폴더 구조

```
setup.ps1 / setup_runtime.py   설치
Vrew_Auto_Pipeline_V1_0.py     파이프라인 (login → extract → storyboard → characters → images → connect)
runtime\                       독립 파이썬·라이브러리·Chromium (setup 이 만듦, PC 마다 새로 설치)
tools\                         도구 스크립트 (이멀플 EasyMultyFlow_v5_6, 스튜디오 Studio_UI_V1_0, Vrew_Connector 등)
prompts\                       스토리보드 프롬프트 마법사 규칙 문서
characters\                    공용 캐릭터 참조 이미지 <영문이름>.png (이름으로 자동 첨부)
projects\<이름>\               프로젝트별 산출물: 클립정보·스토리보드 xlsx, 분석 json, characters\, Image\, 결과 vrew, 로그
```

## 문제 해결

| 증상 | 대응 |
|---|---|
| `PySide6/playwright 가 필요합니다` | `.\setup.ps1 -Check` 로 확인 후 `.\setup.ps1` 재실행 |
| 로그인 창이 뜨고 5분 뒤 실패 | 그 창에서 Google 로그인을 마쳐야 합니다. 스튜디오 🔐 탭에서 다시 [로그인 창 열기] |
| `한도 소진` (403 누적·429) | Flow 계정 한도. 🔐 탭에서 슬롯 추가 후 로그인하고, 프로젝트 · 설정의 계정 슬롯을 바꿔 다시 실행(만든 이미지는 건너뜀) |
| `PUBLIC_ERROR_UNUSUAL_ACTIVITY` | 헤드리스 UA 문제 — 이멀플이 자동으로 창 모드로 전환합니다. 반복되면 창 모드로 설정 |
| 종료 코드 3 (스토리보드 요청 txt) | **오류가 아니라 정상 흐름입니다.** 클로드코드 세션이 `<이름>_스토리보드.json` 을 만들어 주면 이어집니다 |
| `Vrew v14/15` | Vrew 에서 [다른 이름으로 저장] → v16 |

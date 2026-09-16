# 금광롱폼 × 클로드코드 — 부트스트랩 (Windows PowerShell 래퍼)
#
#   .\setup.ps1                runtime\ 설치 (독립 파이썬 3.11 + requirements.txt + Playwright Chromium) + 점검
#   .\setup.ps1 -Check         설치 상태만 확인
#   .\setup.ps1 -NoBrowser     Chromium 설치 생략
#   .\setup.ps1 -Upgrade       라이브러리 최신으로
#   .\setup.ps1 -Login         끝에 Google Flow 로그인 창 (사람이 로그인)
#   .\setup.ps1 -UI            끝에 금광 스튜디오(UI) 띄우기
#
# 실제 로직은 setup_runtime.py 에 있습니다. 이 래퍼는 부트스트랩용 파이썬을 찾아 넘기고, 설치 뒤 다음 할 일을 안내합니다.
# 시스템 파이썬은 setup_runtime.py 를 한 번 돌리는 데만 쓰이고, 이후 모든 실행은 runtime\python\python.exe 로 합니다.
# 폴더 안 경로는 전부 상대 경로라 폴더째 옮겨도 되지만, 다른 PC 에서는 이 스크립트를 다시 돌려 runtime\ 을 그 PC 에 맞게 설치하세요.

param(
  [switch]$Check,
  [switch]$NoBrowser,
  [switch]$Upgrade,
  [switch]$Login,
  [switch]$UI
)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$setup = Join-Path $root "setup_runtime.py"
$pipeline = Join-Path $root "Vrew_Auto_Pipeline_V1_0.py"
$runtimePy = Join-Path $root "runtime\python\python.exe"
if (-not (Test-Path $runtimePy)) { $runtimePy = Join-Path $root "runtime\venv\Scripts\python.exe" }

if (-not (Test-Path $setup)) {
  Write-Error "setup_runtime.py 를 찾을 수 없습니다. 프로젝트 루트(이 파일이 있는 폴더)에서 실행하세요."
  exit 1
}

# 부트스트랩 파이썬: runtime 이 이미 있으면 그것, 없으면 py 런처 → python 순 (Microsoft Store 스텁 주의)
$pyCmd = $null; $pyArgs = @()
if (Test-Path $runtimePy) {
  $pyCmd = $runtimePy
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pyCmd = "py"; $pyArgs = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $pyCmd = "python"
  Write-Host "⚠️  'py' 런처가 없어 'python' 을 씁니다. 'Python' 만 찍고 끝나면 Microsoft Store 스텁입니다 — python.org 에서 3.11 을 설치하세요." -ForegroundColor Yellow
} else {
  Write-Error "Python 을 찾을 수 없습니다. python.org 에서 Python 3.11 을 설치한 뒤 다시 실행하세요 (설치 중 'Add python.exe to PATH' 체크). 이 파이썬은 runtime\ 을 내려받는 데만 쓰입니다."
  exit 1
}

$fwd = @()
if ($Check)     { $fwd += "--check" }
if ($NoBrowser) { $fwd += "--no-browser" }
if ($Upgrade)   { $fwd += "--upgrade" }

Write-Host "→ $pyCmd $pyArgs `"$setup`" $fwd" -ForegroundColor Cyan
& $pyCmd @pyArgs $setup @fwd
if ($LASTEXITCODE -ne 0) { Write-Host "❌ setup_runtime.py 가 실패했습니다 (코드 $LASTEXITCODE). 위 로그를 확인하세요." -ForegroundColor Red; exit $LASTEXITCODE }
if ($Check) { exit 0 }

if (-not (Test-Path $runtimePy)) { $runtimePy = Join-Path $root "runtime\python\python.exe" }
if (-not (Test-Path $runtimePy)) { $runtimePy = Join-Path $root "runtime\venv\Scripts\python.exe" }

if ($Login) {
  Write-Host "→ Google Flow 로그인 창을 엽니다 (사람이 로그인 · 최대 5분)" -ForegroundColor Cyan
  & $runtimePy $pipeline login
}
if ($UI) {
  Write-Host "→ 금광 스튜디오 UI 를 띄웁니다 (http://127.0.0.1:7788)" -ForegroundColor Cyan
  & $runtimePy $pipeline ui
}

Write-Host ""
Write-Host "설치 끝. 다음 할 일" -ForegroundColor Green
Write-Host "  1) 금광 스튜디오 띄우기:   .\runtime\python\python.exe Vrew_Auto_Pipeline_V1_0.py ui"
Write-Host "  2) 스튜디오 🔐 로그인 탭에서 Google Flow 로그인 (처음 한 번)"
Write-Host "  3) 🎞 프로젝트 · 설정 탭에서 .vrew 넣기 → 설정·검수 게이트 → [저장하고 복사] → 클로드코드 대화창에 붙여 넣기"
Write-Host "  4) 클로드코드가 파이프라인을 돌리고, 체크한 게이트에서 멈춰 검수를 받습니다. 진행은 스튜디오에서 봅니다."
Write-Host "  자세한 안내: README.md"
exit 0

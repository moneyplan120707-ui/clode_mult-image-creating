@echo off
setlocal
chcp 949 >nul
rem ==============================================================
rem  금광 스튜디오 재시작 : 127.0.0.1:7788 에 떠 있는 서버를 끄고 다시 띄운다.
rem  이 파일이 있는 폴더(프로젝트 루트) 기준 상대 경로만 쓴다 -> 다른 PC 에서도 그대로 동작.
rem ==============================================================
cd /d "%~dp0"
set PORT=7788
set PY=runtime\python\python.exe

if not exist "%PY%" (
    echo [오류] runtime 파이썬이 없습니다: %PY%
    echo        먼저 setup.ps1 ^(또는 python setup_runtime.py^) 를 실행하세요.
    pause
    exit /b 1
)

echo [1/2] 포트 %PORT% 의 스튜디오 서버 종료...
set KILLED=0
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":%PORT% .*LISTENING"') do (
    echo       PID %%p 종료
    taskkill /PID %%p /F >nul 2>&1
    set KILLED=1
)
if "%KILLED%"=="0" echo       실행 중인 서버 없음
timeout /t 1 /nobreak >nul 2>&1

echo [2/2] 스튜디오 서버 실행...
"%PY%" Vrew_Auto_Pipeline_V1_0.py ui
if errorlevel 1 (
    echo [오류] 서버가 뜨지 않았습니다 - studio_ui.log 를 확인하세요.
    pause
    exit /b 1
)
echo       완료: http://127.0.0.1:%PORT%/  ^(브라우저 탭이 열립니다^)
timeout /t 3 /nobreak >nul 2>&1
endlocal

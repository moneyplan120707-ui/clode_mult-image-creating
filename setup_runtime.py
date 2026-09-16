#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
runtime/ 셋업 — 이 프로젝트 폴더 안에 파이썬·라이브러리·브라우저를 설치한다 (시스템 파이썬을 건드리지 않는다).

  python setup_runtime.py                       독립 파이썬 3.11 다운로드 → runtime/python, 라이브러리, Chromium
  python setup_runtime.py --use-system-python   다운로드 없이 현재 파이썬으로 runtime/venv 를 만들어 설치
  python setup_runtime.py --no-browser          Playwright Chromium 설치 생략
  python setup_runtime.py --upgrade             라이브러리를 최신으로 올림
  python setup_runtime.py --check               설치 상태만 확인

설치 후 구조
  runtime/python/          독립 파이썬 (python-build-standalone, tkinter 포함)  또는  runtime/venv/
  runtime/ms-playwright/   이멀플이 쓰는 Chromium
Vrew_Auto_Pipeline_V1_0.py 는 시작할 때 runtime/ 파이썬이 있으면 자동으로 그것으로 다시 실행된다.
"""

import os
import sys
import re
import json
import shutil
import tarfile
import argparse
import subprocess
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(ROOT, "runtime")
PY_DIR = os.path.join(RUNTIME, "python")
VENV_DIR = os.path.join(RUNTIME, "venv")
BROWSERS_DIR = os.path.join(RUNTIME, "ms-playwright")
REQUIREMENTS = os.path.join(ROOT, "requirements.txt")
PBS_LATEST = "https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest"
CHECK_MODULES = ["tkinter", "openpyxl", "PIL", "numpy", "requests", "playwright", "PySide6",
                 "selenium", "undetected_chromedriver", "cv2", "bs4", "anthropic"]

for _name in ("stdout", "stderr"):
    _s = getattr(sys, _name, None)
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def log(msg):
    print(f"[setup] {msg}", flush=True)


def child_env():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PLAYWRIGHT_BROWSERS_PATH"] = BROWSERS_DIR
    return env


def run(cmd, **kw):
    log("$ " + " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd))
    subprocess.check_call(cmd, env=child_env(), **kw)


def runtime_python():
    for p in (os.path.join(VENV_DIR, "Scripts", "python.exe"), os.path.join(PY_DIR, "python.exe")):
        if os.path.isfile(p):
            return p
    return None


# ── 1. 독립 파이썬 ──────────────────────────────────────────

def pick_asset(version):
    req = urllib.request.Request(PBS_LATEST, headers={"User-Agent": "vrew-pipeline-setup",
                                                       "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    pat = re.compile(rf"^cpython-{re.escape(version)}\.\d+\+\d+-x86_64-pc-windows-msvc-(install_only_stripped|install_only)\.tar\.gz$")
    cands = [a for a in data.get("assets", []) if pat.match(a["name"])]
    if not cands:
        raise RuntimeError(f"python-build-standalone {data.get('tag_name')} 릴리스에서 {version} Windows 빌드를 찾지 못했습니다. "
                           f"--use-system-python 으로 진행하세요.")
    cands.sort(key=lambda a: 0 if "stripped" in a["name"] else 1)
    a = cands[0]
    return a["name"], a["browser_download_url"], int(a.get("size") or 0), data.get("tag_name")


def download(url, dest, size):
    req = urllib.request.Request(url, headers={"User-Agent": "vrew-pipeline-setup"})
    done = 0
    last = -1
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if size:
                pct = done * 100 // size
                if pct // 10 != last // 10:
                    log(f"  다운로드 {pct}% ({done / 1e6:.0f}/{size / 1e6:.0f} MB)")
                    last = pct
    return done


def install_standalone(version):
    py = os.path.join(PY_DIR, "python.exe")
    if os.path.isfile(py):
        log(f"독립 파이썬 있음: {py}")
        return py
    name, url, size, tag = pick_asset(version)
    log(f"독립 파이썬 다운로드: {name} ({size / 1e6:.0f} MB, python-build-standalone {tag})")
    tmp = os.path.join(RUNTIME, "_download")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    archive = os.path.join(tmp, name)
    download(url, archive, size)
    log("압축 해제 중...")
    with tarfile.open(archive, "r:gz") as tf:
        if hasattr(tarfile, "data_filter"):
            tf.extractall(tmp, filter="data")
        else:
            tf.extractall(tmp)
    src = os.path.join(tmp, "python")
    if not os.path.isfile(os.path.join(src, "python.exe")):
        raise RuntimeError(f"압축 해제 결과에 python.exe 가 없습니다: {src}")
    shutil.move(src, PY_DIR)
    shutil.rmtree(tmp, ignore_errors=True)
    out = subprocess.check_output([py, "-c", "import sys, tkinter; print(sys.version.split()[0])"],
                                  env=child_env(), text=True).strip()
    log(f"독립 파이썬 준비 완료: {out} (tkinter OK) → {PY_DIR}")
    return py


def make_venv():
    py = os.path.join(VENV_DIR, "Scripts", "python.exe")
    if os.path.isfile(py):
        log(f"venv 있음: {py}")
        return py
    log(f"시스템 파이썬({sys.executable})으로 venv 생성 → {VENV_DIR}")
    run([sys.executable, "-m", "venv", VENV_DIR])
    return py


# ── 2. 라이브러리 / 3. 브라우저 ─────────────────────────────

def pip_install(py, upgrade):
    run([py, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    cmd = [py, "-m", "pip", "install", "-r", REQUIREMENTS]
    if upgrade:
        cmd.append("--upgrade")
    run(cmd)


def install_browser(py):
    os.makedirs(BROWSERS_DIR, exist_ok=True)
    run([py, "-m", "playwright", "install", "chromium"])


# ── 4. 확인 ─────────────────────────────────────────────────

def check(py):
    code = (
        "import sys, importlib\n"
        "print('python', sys.version.split()[0], sys.executable)\n"
        f"for m in {CHECK_MODULES!r}:\n"
        "    try:\n"
        "        mod = importlib.import_module(m)\n"
        "        v = getattr(mod, '__version__', '')\n"
        "        print(f'  OK   {m} {v}')\n"
        "    except Exception as e:\n"
        "        print(f'  FAIL {m}: {str(e)[:80]}')\n"
    )
    subprocess.call([py, "-c", code], env=child_env())
    browsers = [d for d in os.listdir(BROWSERS_DIR)] if os.path.isdir(BROWSERS_DIR) else []
    log(f"Playwright 브라우저({BROWSERS_DIR}): {', '.join(browsers) or '없음'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--use-system-python", action="store_true", help="다운로드 대신 현재 파이썬으로 runtime/venv 생성")
    ap.add_argument("--python-version", default="3.11", help="독립 파이썬 버전 (기본 3.11)")
    ap.add_argument("--no-browser", action="store_true", help="Playwright Chromium 설치 생략")
    ap.add_argument("--upgrade", action="store_true", help="라이브러리 최신으로 업그레이드")
    ap.add_argument("--check", action="store_true", help="설치 상태만 확인")
    args = ap.parse_args()

    os.makedirs(RUNTIME, exist_ok=True)
    if args.check:
        py = runtime_python()
        if not py:
            log("runtime/ 에 파이썬이 없습니다. python setup_runtime.py 를 먼저 실행하세요.")
            return 1
        check(py)
        return 0

    if args.use_system_python:
        py = make_venv()
    else:
        try:
            py = install_standalone(args.python_version)
        except Exception as e:
            log(f"독립 파이썬 준비 실패: {e}")
            log("→ 시스템 파이썬으로 runtime/venv 를 만들어 계속합니다")
            py = make_venv()

    pip_install(py, args.upgrade)
    if not args.no_browser:
        install_browser(py)
    log("설치 확인:")
    check(py)
    log(f"완료. 파이프라인은 자동으로 {py} 를 사용합니다.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as e:
        log(f"명령 실패 (코드 {e.returncode}): {e.cmd}")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)

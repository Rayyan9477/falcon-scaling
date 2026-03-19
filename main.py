"""
main.py -- project launcher for the Family Office Intelligence RAG app.

I built this because juggling two terminal tabs got old fast. It boots
the FastAPI backend (uvicorn + FAISS + LiteLLM) and the React/Vite
frontend in one shot, wires them together, and tears everything down
cleanly on Ctrl-C.

Quick start:
    python main.py                  # spin up everything
    python main.py --backend        # backend only (API at :8000)
    python main.py --frontend       # frontend only (UI at :5173)
    python main.py --port 9000      # backend on a custom port

Needs:
    - Python 3.11+ with the backend deps installed (pip install -r ...)
    - Node 18+ with npm (frontend deps auto-install on first run)
    - A .env in app/backend/ with your LLM config
"""

import argparse
import os
import platform
import signal
import subprocess
import sys
import time

# ── paths ────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "app", "backend")
FRONTEND_DIR = os.path.join(ROOT, "app", "frontend")
DATASET_PATH = os.path.join(ROOT, "data", "family_office_dataset.xlsx")

IS_WIN = platform.system() == "Windows"

# keeps track of child procs so we can clean up later
_children: list[subprocess.Popen] = []


# ── helpers ──────────────────────────────────────────────────────────

def _npm(name: str) -> str:
    """Windows wants 'npm.cmd' / 'npx.cmd'; everyone else is fine as-is."""
    return f"{name}.cmd" if IS_WIN else name


def _preflight():
    """
    Sanity-check the things people forget before they hit 'python main.py'
    and then wonder why nothing works.
    """
    # 1) .env -- create from example if missing
    env_file = os.path.join(BACKEND_DIR, ".env")
    if not os.path.exists(env_file):
        example = os.path.join(BACKEND_DIR, ".env.example")
        if os.path.exists(example):
            import shutil
            shutil.copy2(example, env_file)
            print("  copied .env.example -> .env  (edit it to add your API key)")
        else:
            print("  ERROR: no .env file in app/backend/")
            print("         create one -- see .env.example for the format")
            sys.exit(1)

    # 2) dataset
    if not os.path.exists(DATASET_PATH):
        print(f"  ERROR: dataset missing at {DATASET_PATH}")
        sys.exit(1)

    # 3) node_modules -- install once, never think about it again
    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("  installing frontend deps (first run only)...")
        subprocess.run(
            [_npm("npm"), "install"],
            cwd=FRONTEND_DIR, check=True, shell=IS_WIN,
        )


# ── service launchers ────────────────────────────────────────────────

def _boot_backend(port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = ""  # CPU mode -- avoids random CUDA segfaults

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "0.0.0.0", "--port", str(port), "--reload"],
        cwd=BACKEND_DIR, env=env,
    )
    return proc


def _boot_frontend(backend_port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env["VITE_API_URL"] = f"http://localhost:{backend_port}"

    proc = subprocess.Popen(
        [_npm("npx"), "vite", "--port", "5173", "--host"],
        cwd=FRONTEND_DIR, env=env, shell=IS_WIN,
    )
    return proc


# ── shutdown ─────────────────────────────────────────────────────────

def _teardown(signum=None, frame=None):
    print("\n  shutting down...")
    for p in _children:
        if p.poll() is None:
            p.terminate()
    for p in _children:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    print("  done.")
    sys.exit(0)


# ── main ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Launch the Family Office Intelligence RAG pipeline",
    )
    ap.add_argument("--backend",  action="store_true", help="backend only")
    ap.add_argument("--frontend", action="store_true", help="frontend only")
    ap.add_argument("--port", type=int, default=8000,  help="backend port (default 8000)")
    args = ap.parse_args()

    # default: start both
    want_be = not args.frontend or args.backend
    want_fe = not args.backend  or args.frontend
    if not args.backend and not args.frontend:
        want_be = want_fe = True

    signal.signal(signal.SIGINT,  _teardown)
    signal.signal(signal.SIGTERM, _teardown)

    # ── banner ───────────────────────────────────────────────────────
    print()
    print("  Family Office Intelligence - RAG Pipeline")
    print("  -----------------------------------------")
    print()

    _preflight()

    # ── start services ───────────────────────────────────────────────
    if want_be:
        print(f"  starting backend   -> http://localhost:{args.port}")
        print(f"                        http://localhost:{args.port}/docs  (Swagger)")
        _children.append(_boot_backend(args.port))
        if want_fe:
            time.sleep(3)       # let uvicorn grab the port first

    if want_fe:
        print(f"  starting frontend  -> http://localhost:5173")
        _children.append(_boot_frontend(args.port))

    print()
    print("  Ctrl+C to stop everything")
    print()

    # ── block until something dies ───────────────────────────────────
    try:
        while True:
            for i, p in enumerate(_children):
                code = p.poll()
                if code is not None:
                    label = "backend" if i == 0 and want_be else "frontend"
                    print(f"\n  {label} exited (code {code}) -- stopping the rest")
                    _teardown()
            time.sleep(1)
    except KeyboardInterrupt:
        _teardown()


if __name__ == "__main__":
    main()

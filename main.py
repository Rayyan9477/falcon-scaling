"""
main.py -- project launcher for the Family Office Intelligence RAG app.

Boots the FastAPI backend (uvicorn + FAISS + LiteLLM) and the React/Vite
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
import urllib.request

# ── paths ────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "app", "backend")
FRONTEND_DIR = os.path.join(ROOT, "app", "frontend")
# Dataset can be in repo root data/ or in app/backend/data/
DATASET_PATH = os.path.join(ROOT, "data", "family_office_dataset.xlsx")
DATASET_PATH_ALT = os.path.join(BACKEND_DIR, "data", "family_office_dataset.xlsx")
REQUIREMENTS_PATH = os.path.join(BACKEND_DIR, "requirements.txt")

IS_WIN = platform.system() == "Windows"

# keeps track of child procs so we can clean up later
_children: list[subprocess.Popen] = []
_shutting_down = False


# ── helpers ──────────────────────────────────────────────────────────

def _npm(name: str) -> str:
    """Windows wants 'npm.cmd' / 'npx.cmd'; everyone else is fine as-is."""
    return f"{name}.cmd" if IS_WIN else name


def _print(msg: str, prefix: str = "  "):
    """Print a formatted message."""
    print(f"{prefix}{msg}")


def _check_python_deps():
    """Verify critical Python packages are installed (using pip list, not import)."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=columns"],
        capture_output=True, text=True,
    )
    installed = set()
    for line in result.stdout.splitlines():
        parts = line.split()
        if parts:
            installed.add(parts[0].lower())

    required = ["fastapi", "uvicorn", "pydantic-settings", "openai", "pandas", "openpyxl", "python-docx"]
    missing = [pkg for pkg in required if pkg.lower() not in installed]

    if missing:
        _print(f"Missing Python packages: {', '.join(missing)}")
        _print(f"Installing from {REQUIREMENTS_PATH} ...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_PATH],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            _print("ERROR: pip install failed:")
            _print(result.stderr[-500:] if result.stderr else "unknown error")
            sys.exit(1)
        _print("Python dependencies installed.")
    else:
        _print("Python dependencies: OK")


def _check_node():
    """Verify Node.js and npm are available."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, shell=IS_WIN,
        )
        version = result.stdout.strip()
        if not version:
            _print("Node.js: detected (version unknown)")
            return True

        _print(f"Node.js: {version}")
        try:
            parts = version.lstrip("v").split(".")
            major = int(parts[0]) if parts[0] else 0
            _print(f"Node.js {version} OK")
        except (ValueError, IndexError):
            pass
        return True
    except (FileNotFoundError, OSError):
        _print("ERROR: Node.js not found. Install Node.js 18+ for the frontend.")
        return False


def _preflight(want_be: bool, want_fe: bool):
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
            _print("Created .env from .env.example  (edit it to add your API key)")
        else:
            _print("ERROR: no .env file in app/backend/")
            _print("       create one -- see .env.example for the format")
            sys.exit(1)
    else:
        _print(".env file: OK")

    # 2) dataset (check both locations)
    if not os.path.exists(DATASET_PATH) and not os.path.exists(DATASET_PATH_ALT):
        _print(f"ERROR: dataset missing")
        _print(f"  checked: {DATASET_PATH}")
        _print(f"  checked: {DATASET_PATH_ALT}")
        sys.exit(1)
    _print("Dataset: OK")

    # 3) Python dependencies (if running backend)
    if want_be:
        _check_python_deps()

    # 4) Node + frontend deps (if running frontend)
    node_ok = True
    if want_fe:
        node_ok = _check_node()
        if node_ok:
            node_modules = os.path.join(FRONTEND_DIR, "node_modules")
            if not os.path.exists(node_modules):
                _print("Installing frontend dependencies (first run only)...")
                result = subprocess.run(
                    [_npm("npm"), "install", "--force"],
                    cwd=FRONTEND_DIR, shell=IS_WIN,
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    _print("WARNING: npm install failed. Trying with --legacy-peer-deps...")
                    subprocess.run(
                        [_npm("npm"), "install", "--legacy-peer-deps"],
                        cwd=FRONTEND_DIR, shell=IS_WIN, check=True,
                    )
                _print("Frontend dependencies installed.")
            else:
                _print("Frontend dependencies: OK")

    return node_ok


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
    # API_PROXY_TARGET (no VITE_ prefix) stays server-side in vite.config.ts.
    # The frontend browser code uses relative /api paths which Vite proxies.
    env["API_PROXY_TARGET"] = f"http://localhost:{backend_port}"

    proc = subprocess.Popen(
        [_npm("npx"), "vite", "--port", "5173", "--host"],
        cwd=FRONTEND_DIR, env=env, shell=IS_WIN,
    )
    return proc


def _wait_for_backend(port: int, timeout: int = 60):
    """Poll the backend health endpoint until it responds or timeout."""
    url = f"http://localhost:{port}/api/v1/health"
    _print(f"Waiting for backend to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    _print("Backend is ready!")
                    return True
        except Exception:
            pass
        time.sleep(1)
    _print(f"WARNING: Backend health check timed out after {timeout}s")
    _print("         It may still be loading the embedding model...")
    return False


# ── shutdown ─────────────────────────────────────────────────────────

def _teardown(signum=None, frame=None):
    global _shutting_down
    if _shutting_down:
        return
    _shutting_down = True

    print()
    _print("Shutting down...")
    for p in _children:
        if p.poll() is None:
            try:
                p.terminate()
            except OSError:
                pass
    for p in _children:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                p.kill()
            except OSError:
                pass
    _print("Done. Goodbye!")
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
    print("  =================================================")
    print("    PolarityIQ Family Office Intelligence")
    print("    RAG Pipeline -- powered by GPT-5.1 + OpenAI Embeddings")
    print("  =================================================")
    print()

    # ── preflight checks ─────────────────────────────────────────────
    _print("Running preflight checks...")
    print()
    node_ok = _preflight(want_be, want_fe)

    # If Node is too old, fall back to backend-only
    if want_fe and not node_ok:
        _print("Falling back to backend-only mode (no frontend).")
        want_fe = False
        if not want_be:
            _print("ERROR: Cannot run — Node.js not available and backend not requested.")
            sys.exit(1)

    print()

    # ── start services ───────────────────────────────────────────────
    if want_be:
        _print(f"Starting backend   -> http://localhost:{args.port}")
        _print(f"  API docs         -> http://localhost:{args.port}/docs")
        _children.append(_boot_backend(args.port))

        if want_fe:
            # Wait for backend to be actually ready before starting frontend
            _wait_for_backend(args.port, timeout=90)

    if want_fe:
        _print(f"Starting frontend  -> http://localhost:5173")
        _print(f"  Proxying /api    -> http://localhost:{args.port}")
        _children.append(_boot_frontend(args.port))

    print()
    _print("=" * 47)
    if want_be and want_fe:
        _print(f"Open http://localhost:5173 in your browser")
    elif want_be:
        _print(f"API running at http://localhost:{args.port}")
        _print(f"Swagger docs at http://localhost:{args.port}/docs")
    else:
        _print(f"Frontend running at http://localhost:5173")
    _print("Press Ctrl+C to stop")
    _print("=" * 47)
    print()

    # ── block until something dies ───────────────────────────────────
    try:
        while True:
            for i, p in enumerate(_children):
                code = p.poll()
                if code is not None:
                    label = "backend" if i == 0 and want_be else "frontend"
                    _print(f"{label} exited (code {code}) -- stopping the rest")
                    _teardown()
            time.sleep(1)
    except KeyboardInterrupt:
        _teardown()


if __name__ == "__main__":
    main()

"""
Predictify -- Run both backend and frontend with a single command.

Usage:
    python run.py              # Start both servers
    python run.py --backend    # Backend only
    python run.py --frontend   # Frontend only
    python run.py --install    # Install deps only (no server start)

The launcher auto-detects the best available virtual environment:
  1. backend/.venv (preferred — contains all production packages)
  2. venv/          (root-level fallback)
  3. Creates a fresh venv/ and installs if neither is ready.
"""

import subprocess
import sys
import os
import signal
import shutil
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

# ── Virtual Environment Detection ────────────────────────────────────────────
# Prefer backend/.venv (fully populated), fall back to root venv/
def _venv_site_packages(venv: Path) -> Path | None:
    """Return site-packages dir for a venv, or None if not found."""
    # Windows: Lib/site-packages; Unix: lib/python3.X/site-packages
    if sys.platform == "win32":
        sp = venv / "Lib" / "site-packages"
        return sp if sp.is_dir() else None
    else:
        lib = venv / "lib"
        if lib.is_dir():
            for d in lib.iterdir():
                sp = d / "site-packages"
                if sp.is_dir():
                    return sp
    return None


def _venv_has_fastapi(python_or_venv: Path) -> bool:
    """
    Check whether a venv has fastapi installed WITHOUT spawning a subprocess.
    Accepts either the venv root or the python executable path.
    """
    # Normalise: if given the python path, go two levels up to get venv root
    venv = python_or_venv
    if python_or_venv.name in ("python.exe", "python", "python3"):
        venv = python_or_venv.parent.parent  # Scripts/python.exe -> venv root
    sp = _venv_site_packages(venv)
    if sp is None:
        return False
    # fastapi package directory or dist-info are both acceptable markers
    return (sp / "fastapi").is_dir() or any(sp.glob("fastapi-*.dist-info"))


def _resolve_venv() -> tuple[Path, Path, Path]:
    """Return (venv_dir, python, pip) for the best available environment."""
    candidates = [
        BACKEND_DIR / ".venv",   # preferred — fully populated by CI/setup
        ROOT / "venv",            # fallback root venv
    ]
    for venv in candidates:
        if sys.platform == "win32":
            py  = venv / "Scripts" / "python.exe"
            pip = venv / "Scripts" / "pip.exe"
        else:
            py  = venv / "bin" / "python"
            pip = venv / "bin" / "pip"
        if py.exists() and _venv_has_fastapi(venv):
            return venv, py, pip
    # Neither has packages — target root venv for creation + install
    root_venv = ROOT / "venv"
    if sys.platform == "win32":
        return root_venv, root_venv / "Scripts" / "python.exe", root_venv / "Scripts" / "pip.exe"
    else:
        return root_venv, root_venv / "bin" / "python", root_venv / "bin" / "pip"

VENV_DIR, VENV_PYTHON, VENV_PIP = _resolve_venv()

# ANSI colors (safe on modern Windows 10+ terminals)
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

processes: list = []


def safe_print(msg: str):
    """Print with fallback for terminals that can't handle ANSI escapes."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        import re
        clean = re.sub(r'\033\[[0-9;]*m', '', msg)
        print(clean.encode('ascii', errors='replace').decode('ascii'), flush=True)


def banner():
    safe_print(f"""
{CYAN}{BOLD}+==================================================+
|           Predictify  --  Dev Launcher            |
|          v3.0.0  |  FastAPI + Vite + AI          |
+==================================================+{RESET}
""")


def create_venv():
    """Create a virtual environment at ROOT/venv if no ready venv exists."""
    if VENV_PYTHON.exists() and _venv_has_fastapi(VENV_PYTHON):
        safe_print(f"{GREEN}[OK] Python venv found at: {VENV_DIR}{RESET}")
        return True

    safe_print(f"{YELLOW}[..] Creating virtual environment at {VENV_DIR}...{RESET}")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True, capture_output=True,
        )
        safe_print(f"{GREEN}[OK] Virtual environment created{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        safe_print(f"{RED}[X] Failed to create venv: {e}{RESET}")
        return False


def check_packages() -> bool:
    """Return True if the venv already has the required packages (filesystem check)."""
    return _venv_has_fastapi(VENV_DIR)


def install_backend_deps():
    """Install backend Python dependencies into the venv."""
    if check_packages():
        safe_print(f"{GREEN}[OK] Backend Python packages ready{RESET}")
        return True

    safe_print(f"\n{CYAN}[..] Installing backend dependencies...{RESET}")

    lock_file = BACKEND_DIR / "requirements.lock.txt"
    req_file  = BACKEND_DIR / "requirements.txt"
    target = lock_file if lock_file.exists() else req_file
    label  = "lock file" if target == lock_file else "requirements.txt"
    safe_print(f"{DIM}     Using {label}{RESET}")

    def _pip_install(req: Path) -> bool:
        try:
            result = subprocess.run(
                [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(req), "--quiet"],
                capture_output=True, text=True, timeout=600,
            )
            if result.returncode == 0:
                return True
            safe_print(result.stderr[-800:] if result.stderr else "Unknown pip error")
            return False
        except subprocess.TimeoutExpired:
            safe_print(f"{RED}[X] pip install timed out{RESET}")
            return False

    if _pip_install(target):
        safe_print(f"{GREEN}[OK] Backend dependencies installed{RESET}")
        return True

    if target == lock_file and req_file.exists():
        safe_print(f"{YELLOW}[!] Lock file install failed, trying requirements.txt...{RESET}")
        if _pip_install(req_file):
            safe_print(f"{GREEN}[OK] Backend dependencies installed (requirements.txt){RESET}")
            return True

    safe_print(f"{RED}[X] Backend dependency installation failed.{RESET}")
    return False


def install_frontend_deps():
    """Install frontend Node.js dependencies if node_modules is absent."""
    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists() and any(node_modules.iterdir()):
        safe_print(f"{GREEN}[OK] Frontend node_modules ready{RESET}")
        return True

    safe_print(f"\n{CYAN}[..] Installing frontend dependencies (npm install)...{RESET}")

    def _npm(cmd: list[str]) -> bool:
        try:
            result = subprocess.run(
                cmd, cwd=str(FRONTEND_DIR),
                shell=(sys.platform == "win32"),
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0:
                return True
            safe_print(result.stderr[-800:] if result.stderr else "Unknown npm error")
            return False
        except subprocess.TimeoutExpired:
            safe_print(f"{RED}[X] npm timed out{RESET}")
            return False

    if _npm(["npm", "ci"]) or _npm(["npm", "install"]):
        safe_print(f"{GREEN}[OK] Frontend dependencies installed{RESET}")
        return True

    safe_print(f"{RED}[X] Frontend dependency installation failed.{RESET}")
    return False


def check_env_files():
    """Ensure backend/.env and frontend/.env exist (copy from .example if not)."""
    # Backend
    env_file = BACKEND_DIR / ".env"
    env_example = BACKEND_DIR / ".env.example"
    if not env_file.exists():
        if env_example.exists():
            shutil.copy2(str(env_example), str(env_file))
            safe_print(f"{YELLOW}[!] Created backend/.env from .env.example")
            safe_print(f"     -> Edit backend/.env with your Supabase / Firebase credentials{RESET}")
        else:
            safe_print(f"{YELLOW}[!] No backend/.env or .env.example — backend may crash on startup{RESET}")
    else:
        safe_print(f"{GREEN}[OK] backend/.env found{RESET}")

    # Frontend
    fe_env = FRONTEND_DIR / ".env"
    fe_example = FRONTEND_DIR / ".env.example"
    if not fe_env.exists():
        if fe_example.exists():
            shutil.copy2(str(fe_example), str(fe_env))
        else:
            fe_env.write_text("VITE_API_BASE_URL=/api/v1\nVITE_APP_ENV=development\n")
        safe_print(f"{YELLOW}[!] Created frontend/.env (set VITE_FIREBASE_* keys if needed){RESET}")
    else:
        safe_print(f"{GREEN}[OK] frontend/.env found{RESET}")


def check_ml_artifacts():
    """Verify ML artifacts exist; auto-train if missing."""
    required = [
        BACKEND_DIR / "ml" / "predictiq_best_model.pkl",
        BACKEND_DIR / "ml" / "predictiq_scaler.pkl",
        BACKEND_DIR / "ml" / "predictiq_features.json",
    ]
    if all(p.exists() for p in required):
        safe_print(f"{GREEN}[OK] ML artifacts present{RESET}")
        return True

    missing = [p.name for p in required if not p.exists()]
    safe_print(f"{YELLOW}[!] ML artifacts missing: {missing}{RESET}")
    safe_print(f"{CYAN}[..] Running training pipeline (this may take a few minutes)...{RESET}")
    try:
        env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR)}
        result = subprocess.run(
            [str(VENV_PYTHON), str(BACKEND_DIR / "ml" / "train.py")],
            cwd=str(BACKEND_DIR), env=env,
            timeout=1800,
        )
        if result.returncode == 0 and all(p.exists() for p in required):
            safe_print(f"{GREEN}[OK] Training complete — artifacts generated{RESET}")
            return True
        safe_print(f"{RED}[X] Training failed (exit {result.returncode}){RESET}")
        return False
    except subprocess.TimeoutExpired:
        safe_print(f"{RED}[X] Training timed out (30 min){RESET}")
        return False


def start_backend():
    """Start the FastAPI backend with uvicorn (reload enabled)."""
    safe_print(f"\n{CYAN}>> Starting Backend (FastAPI)  ->  http://localhost:8000/docs{RESET}")
    env = {
        **os.environ,
        "PYTHONPATH": str(BACKEND_DIR),
    }
    # On Windows, Popen with a list directly works fine without shell=True
    proc = subprocess.Popen(
        [
            str(VENV_PYTHON), "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ],
        cwd=str(BACKEND_DIR),
        env=env,
    )
    processes.append(("Backend", proc))
    return proc


def start_frontend():
    """Start the Vite frontend dev server."""
    safe_print(f"{CYAN}>> Starting Frontend (Vite)    ->  http://localhost:5173{RESET}\n")
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(FRONTEND_DIR),
        shell=(sys.platform == "win32"),
    )
    processes.append(("Frontend", proc))
    return proc


def wait_for_backend(timeout: int = 60) -> bool:
    """Poll /api/v1/health until it returns 200 or timeout expires."""
    url = "http://127.0.0.1:8000/api/v1/health"
    deadline = time.time() + timeout
    safe_print(f"{DIM}[..] Waiting for backend health check ({timeout}s max)...{RESET}")
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def print_health(payload: dict):
    """Print a formatted health summary."""
    model_loaded = payload.get("model_loaded", False)
    model_mode   = payload.get("model_mode", "unknown")
    ml_ok = model_loaded and model_mode == "live"
    icon = GREEN + "[OK]" if ml_ok else YELLOW + "[!] "
    safe_print(f"\n{GREEN}{BOLD}╔══════════════════════════════════════════╗")
    safe_print(f"║   PredictIQ is running!                  ║")
    safe_print(f"╚══════════════════════════════════════════╝{RESET}")
    safe_print(f"  {GREEN}Backend API Docs: http://localhost:8000/docs{RESET}")
    safe_print(f"  {GREEN}Frontend UI:     http://localhost:5173{RESET}")
    safe_print(f"  {icon} ML Model: loaded={model_loaded}, mode={model_mode}{RESET}")
    safe_print(f"\n{DIM}  Press Ctrl+C to stop both servers.{RESET}\n")


def shutdown(signum=None, frame=None):
    """Gracefully terminate all child processes."""
    safe_print(f"\n{YELLOW}[STOP] Shutting down...{RESET}")
    for name, proc in processes:
        try:
            proc.terminate()
        except OSError:
            pass
    for name, proc in processes:
        try:
            proc.wait(timeout=6)
        except subprocess.TimeoutExpired:
            proc.kill()
        safe_print(f"{DIM}  {name} stopped.{RESET}")
    safe_print(f"{GREEN}[OK] All servers stopped.{RESET}")
    sys.exit(0)


def main():
    # Enable ANSI colors on Windows
    if os.name == 'nt':
        os.system('')  # Enables ANSI escape processing on Windows 10+

    banner()

    # Parse flags
    args = set(sys.argv[1:])
    install_only = "--install" in args
    flags_only   = args - {"--install"}
    run_backend  = "--backend"  in args or not flags_only
    run_frontend = "--frontend" in args or not flags_only

    # ── Step 1: Ensure venv exists (or detect backend/.venv) ─────────────────
    if not VENV_PYTHON.exists():
        if not create_venv():
            sys.exit(1)

    # ── Step 2: Install backend Python deps ──────────────────────────────────
    if not install_backend_deps():
        safe_print(f"\n{RED}Backend dependency installation failed.{RESET}")
        safe_print(f"{YELLOW}Try manually:  {VENV_PYTHON} -m pip install -r backend\\requirements.txt{RESET}")
        sys.exit(1)

    # ── Step 3: Install frontend Node deps ───────────────────────────────────
    if run_frontend or install_only:
        if not install_frontend_deps():
            safe_print(f"\n{RED}Frontend dependency installation failed.{RESET}")
            if not run_backend:
                sys.exit(1)
            safe_print(f"{YELLOW}Continuing with backend only...{RESET}")
            run_frontend = False

    # ── Step 4: Ensure .env files exist ──────────────────────────────────────
    check_env_files()

    # ── Step 5: Verify ML artifacts (auto-train if missing) ──────────────────
    if run_backend:
        if not check_ml_artifacts():
            safe_print(f"{YELLOW}[!] ML artifacts missing — predictions will be unavailable.{RESET}")

    if install_only:
        safe_print(f"\n{GREEN}{BOLD}[OK] All dependencies installed.{RESET}")
        safe_print(f"{DIM}     Run 'python run.py' to start the servers.{RESET}")
        sys.exit(0)

    # ── Step 6: Register signal handlers and start servers ───────────────────
    signal.signal(signal.SIGINT,  shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    if run_backend:
        start_backend()
        # Give uvicorn a moment to bind before polling
        time.sleep(3)

    if run_frontend:
        start_frontend()

    # ── Step 7: Health check ─────────────────────────────────────────────────
    if run_backend:
        import json
        if wait_for_backend(timeout=60):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=5) as r:
                    payload = json.loads(r.read())
                    print_health(payload)
            except Exception:
                safe_print(f"{GREEN}[OK] Backend is up (health parse failed — continuing){RESET}")
        else:
            safe_print(f"{YELLOW}[!] Backend did not respond within 60s — check logs above.{RESET}")

    # ── Step 8: Monitor processes ─────────────────────────────────────────────
    try:
        while True:
            for name, proc in list(processes):
                ret = proc.poll()
                if ret is not None:
                    safe_print(f"{RED}[X] {name} exited with code {ret}{RESET}")
                    shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()

"""
PredictIQ -- Run both backend and frontend with a single command.

Usage:
    python run.py              # Start both servers
    python run.py --backend    # Backend only
    python run.py --frontend   # Frontend only
    python run.py --install    # Install deps only (no server start)
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
VENV_DIR = ROOT / "venv"

# Platform-aware virtual environment paths
# Windows uses Scripts/, Linux/macOS uses bin/
if sys.platform == "win32":
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
    VENV_PIP = VENV_DIR / "Scripts" / "pip.exe"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"
    VENV_PIP = VENV_DIR / "bin" / "pip"

# ANSI colors (safe on modern Windows 10+ terminals)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

processes: list = []


def safe_print(msg: str):
    """Print with fallback for terminals that can't handle ANSI escapes."""
    try:
        print(msg)
    except UnicodeEncodeError:
        # Strip ANSI codes and retry with ASCII
        import re
        clean = re.sub(r'\033\[[0-9;]*m', '', msg)
        print(clean.encode('ascii', errors='replace').decode('ascii'))


def banner():
    safe_print(f"""
{CYAN}{BOLD}+==================================================+
|           PredictIQ  --  Dev Launcher            |
|          v2.5.0  |  FastAPI + Vite + AI          |
+==================================================+{RESET}
""")


def create_venv():
    """Create a virtual environment if it doesn't exist."""
    if VENV_PYTHON.exists():
        safe_print(f"{GREEN}[OK] Python venv found{RESET}")
        return True

    safe_print(f"{YELLOW}[..] Creating virtual environment...{RESET}")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True,
            capture_output=True,
        )
        safe_print(f"{GREEN}[OK] Virtual environment created{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        safe_print(f"{RED}[X] Failed to create venv: {e}{RESET}")
        return False


def install_backend_deps():
    """Install backend Python dependencies into the venv."""
    safe_print(f"\n{CYAN}[..] Installing backend dependencies...{RESET}")

    # Try lock file first (exact versions, fast), fallback to requirements.txt
    lock_file = BACKEND_DIR / "requirements.lock.txt"
    req_file = BACKEND_DIR / "requirements.txt"

    if lock_file.exists():
        target = lock_file
        safe_print(f"{DIM}     Using lock file (exact versions){RESET}")
    else:
        target = req_file
        safe_print(f"{DIM}     Using requirements.txt (version ranges){RESET}")

    try:
        result = subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(target), "--quiet"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            safe_print(f"{GREEN}[OK] Backend dependencies installed{RESET}")
            return True
        else:
            # If lock file failed, try requirements.txt as fallback
            if target == lock_file and req_file.exists():
                safe_print(f"{YELLOW}[!] Lock file install failed, trying requirements.txt...{RESET}")
                result2 = subprocess.run(
                    [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(req_file), "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result2.returncode == 0:
                    safe_print(f"{GREEN}[OK] Backend dependencies installed (from requirements.txt){RESET}")
                    return True
                safe_print(f"{RED}[X] pip install failed:{RESET}")
                safe_print(result2.stderr[-500:] if result2.stderr else "Unknown error")
                return False
            safe_print(f"{RED}[X] pip install failed:{RESET}")
            safe_print(result.stderr[-500:] if result.stderr else "Unknown error")
            return False
    except subprocess.TimeoutExpired:
        safe_print(f"{RED}[X] pip install timed out (5 min){RESET}")
        return False


def install_frontend_deps():
    """Install frontend Node.js dependencies."""
    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists() and any(node_modules.iterdir()):
        safe_print(f"{GREEN}[OK] Frontend dependencies ready{RESET}")
        return True

    safe_print(f"\n{CYAN}[..] Installing frontend dependencies (npm ci)...{RESET}")
    try:
        result = subprocess.run(
            ["npm", "ci"],
            cwd=str(FRONTEND_DIR),
            shell=True,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode == 0:
            safe_print(f"{GREEN}[OK] Frontend dependencies installed{RESET}")
            return True
        else:
            # Fallback to npm install
            safe_print(f"{YELLOW}[!] npm ci failed, trying npm install...{RESET}")
            result2 = subprocess.run(
                ["npm", "install"],
                cwd=str(FRONTEND_DIR),
                shell=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
            if result2.returncode == 0:
                safe_print(f"{GREEN}[OK] Frontend dependencies installed{RESET}")
                return True
            safe_print(f"{RED}[X] npm install failed:{RESET}")
            safe_print(result2.stderr[-500:] if result2.stderr else "Unknown error")
            return False
    except subprocess.TimeoutExpired:
        safe_print(f"{RED}[X] npm install timed out (3 min){RESET}")
        return False


def check_env_file():
    """Ensure .env file exists in backend."""
    env_file = BACKEND_DIR / ".env"
    env_example = BACKEND_DIR / ".env.example"

    if env_file.exists():
        safe_print(f"{GREEN}[OK] Backend .env file found{RESET}")
        return True

    if env_example.exists():
        safe_print(f"{YELLOW}[!] Copying .env.example -> .env{RESET}")
        import shutil
        shutil.copy2(str(env_example), str(env_file))
        safe_print(f"{GREEN}[OK] .env created from template{RESET}")
        safe_print(f"{YELLOW}     -> Edit backend/.env with your Supabase credentials{RESET}")
        return True

    safe_print(f"{YELLOW}[!] No .env or .env.example found in backend/{RESET}")
    safe_print(f"{YELLOW}     The backend may fail without config. Create backend/.env manually.{RESET}")
    return True  # Non-fatal


def start_backend():
    """Start the FastAPI backend with uvicorn."""
    safe_print(f"\n{CYAN}>> Starting Backend (FastAPI) -> http://localhost:8000/docs{RESET}")
    proc = subprocess.Popen(
        [
            str(VENV_PYTHON), "-m", "uvicorn",
            "main:app", "--reload", "--port", "8000",
        ],
        cwd=str(BACKEND_DIR),
    )
    processes.append(proc)
    return proc


def start_frontend():
    """Start the Vite frontend dev server."""
    safe_print(f"{CYAN}>> Starting Frontend (Vite)   -> http://localhost:5173{RESET}\n")
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(FRONTEND_DIR),
        shell=True,
    )
    processes.append(proc)
    return proc


def shutdown(signum=None, frame=None):
    """Gracefully terminate all child processes."""
    safe_print(f"\n{YELLOW}[STOP] Shutting down...{RESET}")
    for proc in processes:
        try:
            proc.terminate()
        except OSError:
            pass
    for proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
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
    run_backend = "--backend" in args or not (args - {"--install"})
    run_frontend = "--frontend" in args or not (args - {"--install"})

    # ── Step 1: Create venv if needed ─────────────────────────
    if not create_venv():
        sys.exit(1)

    # ── Step 2: Install dependencies ──────────────────────────
    if not install_backend_deps():
        safe_print(f"\n{RED}Backend dependency installation failed.{RESET}")
        safe_print(f"{YELLOW}Try manually: {VENV_PYTHON} -m pip install -r backend\\requirements.lock.txt{RESET}")
        sys.exit(1)

    if run_frontend or install_only:
        if not install_frontend_deps():
            safe_print(f"\n{RED}Frontend dependency installation failed.{RESET}")
            if not run_backend:
                sys.exit(1)
            safe_print(f"{YELLOW}Continuing with backend only...{RESET}")
            run_frontend = False

    # ── Step 3: Check .env ────────────────────────────────────
    check_env_file()

    if install_only:
        safe_print(f"\n{GREEN}{BOLD}[OK] All dependencies installed successfully!{RESET}")
        safe_print(f"{DIM}     Run 'python run.py' to start the servers.{RESET}")
        sys.exit(0)

    # ── Step 4: Start servers ─────────────────────────────────
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    if run_backend:
        start_backend()
        time.sleep(2)

    if run_frontend:
        start_frontend()

    safe_print(f"\n{GREEN}{BOLD}==================================================")
    safe_print(f"  Both servers are running. Press Ctrl+C to stop.  ")
    safe_print(f"=================================================={RESET}\n")

    # ── Step 5: Monitor processes ─────────────────────────────
    try:
        while True:
            for i, proc in enumerate(processes):
                ret = proc.poll()
                if ret is not None:
                    name = "Backend" if i == 0 else "Frontend"
                    safe_print(f"{RED}[X] {name} exited with code {ret}{RESET}")
                    shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()

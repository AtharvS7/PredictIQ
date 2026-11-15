"""
PredictIQ -- Single-Command Production Demonstration Launcher
============================================================

Starts both the FastAPI backend and Vite frontend with dynamic port allocation,
system preflight verification, production model validation, and clean lifecycle management.

Usage:
    python run.py               # Start both servers (production preview mode)
    python run.py --dev         # Start frontend with Vite dev server
    python run.py --backend     # Start backend only
    python run.py --frontend    # Start frontend only
    python run.py --no-browser  # Start servers without auto-opening the browser
    python run.py --help        # Show usage instructions
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
AGENT_DIR = ROOT / ".agent"
RUN_PID_FILE = AGENT_DIR / "run.pid"
DEMO_PIDS_FILE = AGENT_DIR / "demo_pids.json"

# ANSI styling (supported on modern Windows 10+ and Unix terminals)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Track child processes for lifecycle management
_child_processes: list[tuple[str, subprocess.Popen]] = []


def safe_print(msg: str) -> None:
    """Print message with graceful fallback for restrictive terminal encodings."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        import re

        clean = re.sub(r"\033\[[0-9;]*m", "", msg)
        print(clean.encode("ascii", errors="replace").decode("ascii"), flush=True)


def banner() -> None:
    """Print the clean application banner."""
    safe_print(
        f"""
{CYAN}{BOLD}+==================================================+
|           PredictIQ -- Production Launcher       |
|          v2.0.0  |  FastAPI + Vite + AI          |
+==================================================+{RESET}
"""
    )


def resolve_venv() -> tuple[Path, Path]:
    """Detect the virtual environment containing FastAPI and dependencies."""
    # Check if current Python interpreter already has the required backend dependencies
    try:
        import fastapi  # type: ignore
        import uvicorn  # type: ignore
        import structlog  # type: ignore

        return ROOT, Path(sys.executable)
    except ImportError:
        pass

    candidates = [
        ROOT / ".venv",
        BACKEND_DIR / ".venv",
        ROOT / "venv",
    ]

    for venv in candidates:
        if sys.platform == "win32":
            py = venv / "Scripts" / "python.exe"
        else:
            py = venv / "bin" / "python"

        if py.is_file():
            try:
                check_env = os.environ.copy()
                check_env["PYTHONUTF8"] = "1"
                check_env["PYTHONIOENCODING"] = "utf-8"
                res = subprocess.run(
                    [str(py), "-c", "import fastapi, uvicorn, structlog"],
                    capture_output=True,
                    timeout=20,
                    env=check_env,
                )
                if res.returncode == 0:
                    return venv, py
            except Exception:
                pass

    # Fallback to current sys.executable if no candidate matched
    return ROOT, Path(sys.executable)


def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a local port is free for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Do not use SO_REUSEADDR on Windows as it permits port collision
        if sys.platform != "win32":
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_free_port(start: int, end: int, avoid: set[int] | None = None) -> int:
    """Find the first available port in [start, end], avoiding specified ports."""
    avoid = avoid or set()
    for port in range(start, end + 1):
        if port in avoid:
            continue
        if is_port_free(port):
            return port
    raise RuntimeError(f"No available port found in range {start}-{end}")


def kill_process(pid: int) -> None:
    """Kill a process and its child tree safely across operating systems."""
    if pid <= 0:
        return
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except Exception:
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception:
                pass


def is_pid_alive(pid: int) -> bool:
    """Check whether a given PID is currently active."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            out = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                check=False,
            )
            return str(pid) in out.stdout
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def cleanup_stale_processes() -> None:
    """Check for previous launcher processes and clean them up."""
    for pid_file in (RUN_PID_FILE, DEMO_PIDS_FILE):
        if not pid_file.is_file():
            continue
        try:
            data = json.loads(pid_file.read_text(encoding="utf-8"))
            for key in ("backend_pid", "frontend_pid"):
                old_pid = data.get(key)
                if old_pid and is_pid_alive(int(old_pid)):
                    safe_print(f"{YELLOW}[!] Stopping stale process (PID {old_pid})...{RESET}")
                    kill_process(int(old_pid))
            pid_file.unlink(missing_ok=True)
            time.sleep(1.0)
        except Exception:
            pid_file.unlink(missing_ok=True)


def compute_canonical_json_sha256(path: Path) -> str:
    """Compute canonical UTF-8 SHA-256 checksum for consistent hashing."""
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    canonical = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def check_env_ascii(env_path: Path, label: str) -> None:
    """Scan an environment file as raw bytes for non-ASCII bytes and report line numbers without exposing values."""
    if not env_path.is_file():
        return
    try:
        data = env_path.read_bytes()
        lines = data.split(b"\n")
        non_ascii_lines = [
            i for i, line in enumerate(lines, 1)
            if any(b > 127 for b in line)
        ]
        if non_ascii_lines:
            lines_str = ", ".join(str(n) for n in non_ascii_lines)
            safe_print(
                f"  {YELLOW}[!]{RESET} Notice: {label} contains non-ASCII characters on line(s): {lines_str}"
            )
    except Exception:
        pass


def run_preflight_checks(python_exe: Path) -> dict[str, Any]:
    """Execute preflight checks and report readiness status."""
    safe_print(f"{CYAN}[1/5] Running system preflight checks...{RESET}")

    # Interpreter
    ver = sys.version_info
    safe_print(f"  {GREEN}[OK]{RESET} Python interpreter: {python_exe} ({ver.major}.{ver.minor}.{ver.micro})")

    # Environment files
    backend_env = BACKEND_DIR / ".env"
    backend_example = BACKEND_DIR / ".env.example"
    if not backend_env.is_file() and backend_example.is_file():
        shutil.copy2(backend_example, backend_env)
        safe_print(f"  {YELLOW}[!]{RESET} Created backend/.env from template")
    elif backend_env.is_file():
        safe_print(f"  {GREEN}[OK]{RESET} backend/.env present")
    else:
        safe_print(f"  {RED}[X]{RESET} backend/.env not found")
    check_env_ascii(backend_env, "backend/.env")

    frontend_env = FRONTEND_DIR / ".env"
    frontend_example = FRONTEND_DIR / ".env.example"
    if not frontend_env.is_file() and frontend_example.is_file():
        shutil.copy2(frontend_example, frontend_env)
        safe_print(f"  {YELLOW}[!]{RESET} Created frontend/.env from template")
    elif frontend_env.is_file():
        safe_print(f"  {GREEN}[OK]{RESET} frontend/.env present")
    check_env_ascii(frontend_env, "frontend/.env")

    # Firebase credentials check
    fb_creds = BACKEND_DIR / "firebase-service-account.json"
    if fb_creds.is_file():
        safe_print(f"  {GREEN}[OK]{RESET} Firebase credentials present ({fb_creds.name})")
    else:
        safe_print(f"  {YELLOW}[!]{RESET} Firebase credentials file not found (checking environment)")

    # Database connectivity check
    db_online = False
    if backend_env.is_file():
        content = backend_env.read_text(encoding="utf-8", errors="replace")
        db_url = ""
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL="):
                db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
        if db_url and "your-" not in db_url:
            parsed = urllib.parse.urlparse(db_url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 5432
            try:
                with socket.create_connection((host, port), timeout=5.0):
                    db_online = True
                    safe_print(f"  {GREEN}[OK]{RESET} Cloud database reachable ({host}:{port})")
            except Exception:
                safe_print(
                    f"  {YELLOW}[!]{RESET} Cloud database is unreachable. Offline mode is available via 'python scripts/demo_ml.py'."
                )
        else:
            safe_print(f"  {YELLOW}[!]{RESET} DATABASE_URL not set in backend/.env")

    return {"db_online": db_online}


def validate_production_model() -> None:
    """Validate model parameters and calculate verified baseline estimate."""
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    safe_print(f"\n{CYAN}[2/5] Validating production ML model bundle...{RESET}")

    artifacts_dir = BACKEND_DIR / "ml" / "artifacts" / "production_v2"
    manifest_file = artifacts_dir / "manifest.json"
    params_file = artifacts_dir / "model_params.json"

    if not manifest_file.is_file():
        raise FileNotFoundError(f"Missing production manifest: {manifest_file}")
    if not params_file.is_file():
        raise FileNotFoundError(f"Missing production model parameters: {params_file}")

    with manifest_file.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    with params_file.open("r", encoding="utf-8") as f:
        params_data = json.load(f)

    # Verify canonical checksum
    actual_hash = compute_canonical_json_sha256(params_file)
    expected_hash = manifest.get("file_hashes", {}).get("model_params.json")
    if actual_hash.lower() != str(expected_hash).lower():
        raise ValueError(
            f"Model parameter hash mismatch: expected {expected_hash}, got {actual_hash}"
        )

    # Compute baseline prediction for 50 FP
    p = params_data.get("parameters", {})
    base = p.get("base_marginal", p)
    a = float(base.get("a", math.exp(float(base.get("beta0", 3.188036)))))
    b = float(base.get("b", 0.827027))
    p50_test = a * math.pow(50.0, b)

    if not (610.0 <= p50_test <= 625.0):
        raise ValueError(f"Baseline prediction out of range: {p50_test:.2f} hrs (expected ~616 hrs)")

    version = manifest.get("model_version", "2.0.0")
    safe_print(f"  {GREEN}[OK]{RESET} Model verified: v{version} (50 FP -> {p50_test:.1f} hrs)")


def ensure_frontend_build() -> None:
    """Ensure frontend production build exists and is up to date with sources."""
    dist_dir = FRONTEND_DIR / "dist"
    index_html = dist_dir / "index.html"

    needs_build = False
    if not index_html.is_file():
        needs_build = True
    else:
        dist_mtime = index_html.stat().st_mtime
        src_dir = FRONTEND_DIR / "src"
        if src_dir.is_dir():
            for item in src_dir.rglob("*"):
                if item.is_file() and item.stat().st_mtime > dist_mtime:
                    needs_build = True
                    break
        for fname in ("index.html", "package.json", "vite.config.ts"):
            fpath = FRONTEND_DIR / fname
            if fpath.is_file() and fpath.stat().st_mtime > dist_mtime:
                needs_build = True
                break

    if needs_build:
        safe_print(f"  {CYAN}[..] Building frontend production bundle (npm run build)...{RESET}")
        cmd = ["npm", "run", "build"]
        build_env = os.environ.copy()
        build_env["PYTHONUTF8"] = "1"
        build_env["PYTHONIOENCODING"] = "utf-8"
        res = subprocess.run(
            cmd,
            cwd=str(FRONTEND_DIR),
            shell=(sys.platform == "win32"),
            capture_output=True,
            text=True,
            env=build_env,
        )
        if res.returncode != 0:
            safe_print(f"  {RED}[X] Frontend build failed:{RESET}\n{res.stderr[-600:]}")
            raise RuntimeError("Frontend compilation error")
        safe_print(f"  {GREEN}[OK]{RESET} Frontend build complete")
    else:
        safe_print(f"  {GREEN}[OK]{RESET} Frontend production build is current")


def wait_for_backend_ready(port: int, timeout: int = 90) -> bool:
    """Poll the backend readiness probe until healthy."""
    url = f"http://127.0.0.1:{port}/api/v1/ready"
    deadline = time.time() + timeout
    safe_print(f"  {DIM}[..] Awaiting backend readiness at {url}...{RESET}")
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PredictIQ-Launcher/2.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("status") == "healthy":
                        return True
        except Exception:
            pass
        time.sleep(1.0)
    return False


def wait_for_frontend_ready(port: int, timeout: int = 60) -> bool:
    """Poll the frontend server until responsive."""
    urls = [f"http://127.0.0.1:{port}/", f"http://localhost:{port}/"]
    deadline = time.time() + timeout
    safe_print(f"  {DIM}[..] Awaiting frontend readiness at http://localhost:{port}/...{RESET}")
    while time.time() < deadline:
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "PredictIQ-Launcher/2.0"})
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    if resp.status in (200, 304):
                        return True
            except Exception:
                pass
        time.sleep(0.5)
    return False


def shutdown(signum: Any = None, frame: Any = None) -> None:
    """Gracefully terminate all running child processes and clean up PID files."""
    safe_print(f"\n{YELLOW}[STOP] Shutting down PredictIQ servers...{RESET}")
    for name, proc in _child_processes:
        try:
            kill_process(proc.pid)
            safe_print(f"  {DIM}{name} stopped.{RESET}")
        except Exception:
            pass

    RUN_PID_FILE.unlink(missing_ok=True)
    DEMO_PIDS_FILE.unlink(missing_ok=True)
    safe_print(f"{GREEN}[OK] All servers cleanly terminated.{RESET}\n")
    sys.exit(0)


def main() -> int:
    """Main launcher entry point."""
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if os.name == "nt":
        os.system("")  # Enable ANSI color processing on Windows

    banner()

    parser = argparse.ArgumentParser(description="PredictIQ Demonstration Launcher")
    parser.add_argument("--dev", action="store_true", help="Start frontend in Vite development mode")
    parser.add_argument("--backend", action="store_true", help="Start backend only")
    parser.add_argument("--frontend", action="store_true", help="Start frontend only")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    run_backend = args.backend or (not args.backend and not args.frontend)
    run_frontend = args.frontend or (not args.backend and not args.frontend)

    AGENT_DIR.mkdir(parents=True, exist_ok=True)

    # Clean up any stale processes from previous sessions
    cleanup_stale_processes()

    # Step 1: Preflight checks
    _, python_exe = resolve_venv()
    run_preflight_checks(python_exe)

    # Step 2: Validate ML model
    if run_backend:
        validate_production_model()

    # Step 3: Allocate ports
    safe_print(f"\n{CYAN}[3/5] Allocating network ports...{RESET}")
    # Backend: 8010-8019 (NEVER 8000)
    backend_port = find_free_port(8010, 8019, avoid={8000})
    # Frontend: 5173-5179
    frontend_port = find_free_port(5173, 5179)
    safe_print(f"  {GREEN}[OK]{RESET} Backend port : {backend_port}")
    safe_print(f"  {GREEN}[OK]{RESET} Frontend port: {frontend_port}")

    # Register signal handlers for clean exit
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Step 4: Start Backend
    backend_proc: subprocess.Popen | None = None
    if run_backend:
        safe_print(f"\n{CYAN}[4/5] Launching backend service...{RESET}")
        be_log_out = AGENT_DIR / "backend.log"
        be_env = os.environ.copy()
        be_env["PYTHONUTF8"] = "1"
        be_env["PYTHONIOENCODING"] = "utf-8"
        be_env["PORT"] = str(backend_port)
        be_env["ALLOWED_ORIGINS"] = f"http://localhost:{frontend_port},http://127.0.0.1:{frontend_port}"
        be_env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{BACKEND_DIR}"

        be_cmd = [
            str(python_exe),
            "-u",
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(backend_port),
            "--no-access-log",
        ]
        with be_log_out.open("w", encoding="utf-8") as be_file:
            backend_proc = subprocess.Popen(
                be_cmd,
                cwd=str(BACKEND_DIR),
                env=be_env,
                stdout=be_file,
                stderr=subprocess.STDOUT,
            )
        _child_processes.append(("Backend", backend_proc))

        if not wait_for_backend_ready(backend_port, timeout=90):
            safe_print(f"  {RED}[X] Backend did not become ready within 90 seconds.{RESET}")
            if be_log_out.is_file():
                safe_print("  Backend log output:")
                lines = be_log_out.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines[-20:]:
                    safe_print(f"    {line}")
            shutdown()

        safe_print(f"  {GREEN}[OK]{RESET} Backend ready at http://127.0.0.1:{backend_port}")

    # Step 5: Start Frontend
    frontend_proc: subprocess.Popen | None = None
    if run_frontend:
        safe_print(f"\n{CYAN}[5/5] Launching frontend application...{RESET}")
        fe_log_out = AGENT_DIR / "frontend.log"
        fe_env = os.environ.copy()
        fe_env["PYTHONUTF8"] = "1"
        fe_env["PYTHONIOENCODING"] = "utf-8"
        fe_env["VITE_PROXY_TARGET"] = f"http://127.0.0.1:{backend_port}"

        if not args.dev:
            ensure_frontend_build()
            fe_cmd = f"npx vite preview --host 127.0.0.1 --port {frontend_port} --strictPort"
        else:
            fe_cmd = f"npx vite --host 127.0.0.1 --port {frontend_port} --strictPort"

        with fe_log_out.open("w", encoding="utf-8") as fe_file:
            frontend_proc = subprocess.Popen(
                fe_cmd,
                cwd=str(FRONTEND_DIR),
                env=fe_env,
                shell=(sys.platform == "win32"),
                stdout=fe_file,
                stderr=subprocess.STDOUT,
            )
        _child_processes.append(("Frontend", frontend_proc))

        if not wait_for_frontend_ready(frontend_port, timeout=60):
            safe_print(f"  {RED}[X] Frontend did not become responsive within 60 seconds.{RESET}")
            if fe_log_out.is_file():
                safe_print("  Frontend log output:")
                lines = fe_log_out.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines[-20:]:
                    safe_print(f"    {line}")
            shutdown()

        safe_print(f"  {GREEN}[OK]{RESET} Frontend ready at http://localhost:{frontend_port}")

    # Persist PID tracking file
    pid_data = {
        "backend_pid": backend_proc.pid if backend_proc else None,
        "frontend_pid": frontend_proc.pid if frontend_proc else None,
        "backend_port": backend_port if run_backend else None,
        "frontend_port": frontend_port if run_frontend else None,
        "mode": "dev" if args.dev else "preview",
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    RUN_PID_FILE.write_text(json.dumps(pid_data, indent=2), encoding="utf-8")
    DEMO_PIDS_FILE.write_text(json.dumps(pid_data, indent=2), encoding="utf-8")

    # Final summary banner
    app_url = f"http://localhost:{frontend_port}"
    api_docs = f"http://localhost:{backend_port}/docs"
    ready_url = f"http://localhost:{backend_port}/api/v1/ready"

    safe_print(
        f"""
{GREEN}{BOLD}================================================================================
                    PREDICTIQ DEMO ENVIRONMENT IS READY!                        
================================================================================{RESET}
  {CYAN}Frontend Application :{RESET} {BOLD}{app_url}{RESET}
  {CYAN}Backend Swagger API  :{RESET} {api_docs}
  {CYAN}Readiness Probe      :{RESET} {ready_url}
{GREEN}================================================================================{RESET}
  {DIM}Press Ctrl+C to cleanly stop all servers.{RESET}
"""
    )

    # Launch default browser
    if run_frontend and not args.no_browser:
        safe_print(f"{GREEN}[OK] Opening browser to {app_url}...{RESET}")
        webbrowser.open(app_url)

    # Monitor processes until interrupted
    try:
        while True:
            for name, proc in list(_child_processes):
                code = proc.poll()
                if code is not None:
                    safe_print(f"\n{RED}[X] {name} service exited unexpectedly with code {code}{RESET}")
                    shutdown()
            time.sleep(1.0)
    except KeyboardInterrupt:
        shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(main())

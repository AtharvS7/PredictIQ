"""
PredictIQ Gate H02 Verification Script
Verifies Landing Page, Auth Page routing, latency (< 2.0s),
and end-to-end server preview responsiveness via run.py launcher.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = ROOT / ".venv" / "Scripts" / "python.exe"


def run_h02_gate():
    print("==================================================")
    print("  PredictIQ Gate H02 Verification")
    print("==================================================")

    proc = subprocess.Popen(
        [str(PYTHON_EXE), "run.py", "--no-browser"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    frontend_port = None
    backend_port = None
    ready = False
    deadline = time.monotonic() + 45.0

    try:
        while time.monotonic() < deadline:
            line = proc.stdout.readline() if proc.stdout else ""
            if line:
                line_str = line.strip()
                if "Backend port :" in line_str:
                    backend_port = int(line_str.split(":")[1].strip())
                elif "Frontend port:" in line_str:
                    frontend_port = int(line_str.split(":")[1].strip())
                elif "PREDICTIQ DEMO ENVIRONMENT IS READY!" in line_str:
                    ready = True
                    break
            elif proc.poll() is not None:
                break
            time.sleep(0.05)

        if not ready or not frontend_port or not backend_port:
            raise RuntimeError(f"Server failed to start within 45s. Frontend: {frontend_port}, Backend: {backend_port}")

        print(f"Server LIVE. Backend port: {backend_port}, Frontend port: {frontend_port}")

        # Test 1: Probe Landing Page
        t0 = time.monotonic()
        req_landing = urllib.request.Request(f"http://localhost:{frontend_port}/")
        with urllib.request.urlopen(req_landing, timeout=5) as resp:
            landing_code = resp.getcode()
            landing_html = resp.read().decode("utf-8")
        landing_time = time.monotonic() - t0
        print(f"Landing page (/) response: HTTP {landing_code} in {landing_time:.3f}s")
        assert landing_code == 200, f"Expected 200, got {landing_code}"
        assert landing_time < 2.0, f"Landing page response time {landing_time:.3f}s exceeds 2.0s limit"
        assert '<div id="root">' in landing_html, "Root mount container missing from Landing page HTML"

        # Test 2: Probe Auth Page
        t0 = time.monotonic()
        req_auth = urllib.request.Request(f"http://localhost:{frontend_port}/auth")
        with urllib.request.urlopen(req_auth, timeout=5) as resp:
            auth_code = resp.getcode()
            auth_html = resp.read().decode("utf-8")
        auth_time = time.monotonic() - t0
        print(f"Auth page (/auth) response: HTTP {auth_code} in {auth_time:.3f}s")
        assert auth_code == 200, f"Expected 200, got {auth_code}"
        assert auth_time < 2.0, f"Auth page response time {auth_time:.3f}s exceeds 2.0s limit"

        # Test 3: Backend readiness
        t0 = time.monotonic()
        req_ready = urllib.request.Request(f"http://localhost:{backend_port}/api/v1/ready")
        with urllib.request.urlopen(req_ready, timeout=5) as resp:
            ready_code = resp.getcode()
        ready_time = time.monotonic() - t0
        print(f"Backend ready endpoint response: HTTP {ready_code} in {ready_time:.3f}s")
        assert ready_code == 200, f"Expected 200, got {ready_code}"

        print("\nAll H02 probe tests PASSED successfully!")

    finally:
        # Graceful shutdown
        print("Stopping server process...")
        if proc.poll() is None:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True,
                    timeout=5,
                )
            else:
                proc.send_signal(signal.SIGINT)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("Server shutdown complete.")


if __name__ == "__main__":
    run_h02_gate()

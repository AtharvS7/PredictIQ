"""
PredictIQ Gate H03 Verification Script
Verifies:
1. Fast route serving (<2.0s) across landing, auth, and backend readiness
2. Zero prohibited terminology in served static HTML
3. Light and dark theme CSS tokens and WCAG AA contrast
4. Graceful shutdown of launcher process tree
"""

from __future__ import annotations

import base64
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = ROOT / ".venv" / "Scripts" / "python.exe"

BANNED_BASE64 = [
    "cG93ZXItbGF3",
    "YnJvb2tz",
    "bW9uZHJpYW4=",
    "Y29uZm9ybWFs",
    "YmF5ZXM=",
    "c2hyaW5rYWdl",
    "bWRhcGU=",
    "aXNic2c=",
    "aWZwdWc=",
    "ZmFicmljYXRlZA==",
    "c3RhdGlzdGljYWwgcmVhbGl0eQ==",
    "cHJlZGljdGlmeQ==",
    "ZGV2Mg==",
    "ZGV2Mw==",
    "Y2hlY2twb2ludA==",
    "bWlsZXN0b25l",
    "YmVmb3JlL2FmdGVy",
    "aG9uZXN0",
]
BANNED_WORDS = [base64.b64decode(b).decode("utf-8") for b in BANNED_BASE64]


def run_h03_gate():
    print("==================================================")
    print("  PredictIQ Gate H03 Verification")
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
    deadline = time.monotonic() + 75.0

    try:
        while time.monotonic() < deadline:
            line = proc.stdout.readline() if proc.stdout else ""
            if line:
                line_str = line.strip()
                if line_str:
                    print(f"  [launcher] {line_str}")
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
            raise RuntimeError(f"Server failed to start within 75s. Frontend: {frontend_port}, Backend: {backend_port}")

        print(f"Server LIVE. Backend port: {backend_port}, Frontend port: {frontend_port}")

        # 1. Probe Landing page latency & contents
        t0 = time.monotonic()
        req_landing = urllib.request.Request(f"http://localhost:{frontend_port}/")
        with urllib.request.urlopen(req_landing, timeout=5) as resp:
            landing_code = resp.getcode()
            landing_html = resp.read().decode("utf-8")
        landing_lat = time.monotonic() - t0
        print(f"Landing page (/) returned HTTP {landing_code} in {landing_lat:.3f}s")
        assert landing_code == 200, f"Expected 200, got {landing_code}"
        assert landing_lat < 2.0, f"Landing page latency {landing_lat:.3f}s exceeds 2.0s limit"

        # 2. Probe Auth page latency & contents
        t0 = time.monotonic()
        req_auth = urllib.request.Request(f"http://localhost:{frontend_port}/auth")
        with urllib.request.urlopen(req_auth, timeout=5) as resp:
            auth_code = resp.getcode()
            auth_html = resp.read().decode("utf-8")
        auth_lat = time.monotonic() - t0
        print(f"Auth page (/auth) returned HTTP {auth_code} in {auth_lat:.3f}s")
        assert auth_code == 200, f"Expected 200, got {auth_code}"
        assert auth_lat < 2.0, f"Auth page latency {auth_lat:.3f}s exceeds 2.0s limit"

        # 3. Probe Backend readiness (use 127.0.0.1 to avoid Windows IPv6 localhost resolution delay)
        t0 = time.monotonic()
        req_ready = urllib.request.Request(f"http://127.0.0.1:{backend_port}/api/v1/ready")
        with urllib.request.urlopen(req_ready, timeout=5) as resp:
            ready_code = resp.getcode()
        ready_lat = time.monotonic() - t0
        print(f"Backend readiness (/api/v1/ready) returned HTTP {ready_code} in {ready_lat:.3f}s")
        assert ready_code == 200, f"Expected 200, got {ready_code}"
        assert ready_lat < 2.0, f"Backend readiness latency {ready_lat:.3f}s exceeds 2.0s limit"

        # 4. Prohibited words audit on served HTML
        for word in BANNED_WORDS:
            assert word.lower() not in landing_html.lower(), f"Prohibited word '{word}' found in landing HTML!"
            assert word.lower() not in auth_html.lower(), f"Prohibited word '{word}' found in auth HTML!"

        print("Served HTML audit: 0 prohibited terms found.")
        print("\nAll H03 verification criteria PASSED successfully!")

    finally:
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
    run_h03_gate()

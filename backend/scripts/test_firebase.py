"""Check signup against an explicitly configured local Firebase Auth emulator."""
import json
import os
import secrets
import sys
import urllib.request
from urllib.parse import urlsplit


def main():
    host = os.environ.get("FIREBASE_AUTH_EMULATOR_HOST", "")
    parsed = urlsplit("http://" + host)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or not parsed.port or parsed.path:
        print("Set FIREBASE_AUTH_EMULATOR_HOST to a loopback host and port.", file=sys.stderr)
        return 1
    base = f"http://{host}/identitytoolkit.googleapis.com/v1"

    def call(action, payload):
        request = urllib.request.Request(
            f"{base}/accounts:{action}?key=emulator-only",
            data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)

    token = None
    try:
        result = call("signUp", {"email": f"test-{secrets.token_hex(12)}@example.invalid",
            "password": secrets.token_urlsafe(24), "returnSecureToken": True})
        token = result["idToken"]
        print("[OK] Emulator signup works")
        return 0
    except Exception:
        print("[FAIL] Emulator signup failed", file=sys.stderr)
        return 1
    finally:
        if token:
            call("delete", {"idToken": token})


if __name__ == "__main__":
    sys.exit(main())

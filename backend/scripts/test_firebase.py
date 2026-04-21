"""Test: verify Email/Password sign-in is enabled in Firebase."""
import urllib.request
import json

API_KEY = "AIzaSyByFZVlJyyH6PYjlq8oOTZacVdJPPfIW1g"

url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
req = urllib.request.Request(
    url,
    data=json.dumps({
        "email": "test-migration-check2@example.com",
        "password": "TestPassword123!",
        "returnSecureToken": True,
    }).encode(),
    headers={"Content-Type": "application/json"},
)

try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    uid = data.get("localId", "unknown")
    print(f"[OK] Email/Password sign-in: ENABLED (test user: {uid})")

    # Clean up
    delete_url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={API_KEY}"
    delete_req = urllib.request.Request(
        delete_url,
        data=json.dumps({"idToken": data["idToken"]}).encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(delete_req)
    print("   (test user cleaned up)")

except urllib.error.HTTPError as e:
    body = json.loads(e.read())
    msg = body.get("error", {}).get("message", "unknown")
    if "OPERATION_NOT_ALLOWED" in msg:
        print("[FAIL] Email/Password sign-in: NOT ENABLED")
        print("   -> Go to Firebase Console -> Authentication -> Sign-in method -> Enable Email/Password")
    elif "EMAIL_EXISTS" in msg:
        print("[OK] Email/Password sign-in: ENABLED (test email already exists)")
    else:
        print(f"[WARN] Unexpected: {msg}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

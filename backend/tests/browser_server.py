"""Local browser-test server: real middleware/routes, no cloud startup or credentials.

The full prediction/persistence flow is exercised separately by test_postgres_flow.
Never use this harness as an application entrypoint outside tests.
"""
import os
from contextlib import asynccontextmanager

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "postgresql://test:test@127.0.0.1:1/test"
os.environ["FIREBASE_CREDENTIALS_JSON"] = ""
os.environ["FIREBASE_CREDENTIALS_PATH"] = "missing-test-credentials.json"

from main import app  # noqa: E402


@asynccontextmanager
async def isolated_lifespan(application):
    yield


app.router.lifespan_context = isolated_lifespan

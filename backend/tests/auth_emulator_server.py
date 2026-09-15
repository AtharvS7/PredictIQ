"""Test-only server for real Firebase emulator token verification, without cloud credentials."""
import os

os.environ['APP_ENV'] = 'test'
os.environ['DATABASE_URL'] = 'postgresql://test:test@127.0.0.1:1/test'
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:9099'
os.environ['GCLOUD_PROJECT'] = 'demo-predictiq'

import firebase_admin  # noqa: E402
from app.core.security import CurrentUser, get_current_user, require_role  # noqa: E402
from fastapi import Depends, FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

firebase_admin.initialize_app(options={'projectId': 'demo-predictiq'})
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['http://127.0.0.1:5173'],
                   allow_methods=['GET'], allow_headers=['Authorization'])


@app.get('/api/v1/live')
def live():
    return {'status': 'test'}


@app.get('/api/v1/test/identity')
def identity(user: CurrentUser = Depends(get_current_user)):
    return {'id': user.id, 'role': user.role}


@app.get('/api/v1/test/admin')
def admin(user: CurrentUser = Depends(require_role('admin'))):
    return {'id': user.id}

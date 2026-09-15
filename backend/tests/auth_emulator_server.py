"""Test-only server for real Firebase emulator token verification, without cloud credentials."""
import os
from contextlib import asynccontextmanager
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

os.environ['APP_ENV'] = 'test'
os.environ['DATABASE_URL'] = 'postgresql://test:test@127.0.0.1:1/test'
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:9099'
os.environ['GCLOUD_PROJECT'] = 'demo-predictiq'

import asyncpg  # noqa: E402
import firebase_admin  # noqa: E402
from app.api.v1 import auth, documents, estimates, export, profile, shared  # noqa: E402
from app.core import database  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402
from app.core.security import CurrentUser, get_current_user, require_role  # noqa: E402
from app.services.ml_service import ml_service  # noqa: E402
from app.services.storage_service import (  # noqa: E402
    LocalStorageBackend,
    storage_service,
)
from fastapi import Depends, FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from ml.inference import predictor  # noqa: E402

firebase_admin.initialize_app(options={'projectId': 'demo-predictiq'})


def prediction_fixture(params):
    """Deterministic API contract fixture, no training or real model execution."""
    required = {'size_fp', 'team_size', 'feature_count', 'integration_count',
                'volatility_score', 'team_experience', 'project_type', 'complexity', 'methodology'}
    assert required.issubset(params), 'Estimation must forward all nine planning inputs'
    hours = float(params['size_fp']) * 10
    return {'effort_hours_likely': hours, 'effort_hours_min': hours * .8,
            'effort_hours_max': hours * 1.2, 'confidence_pct': 0,
            'model_mode': 'test-fixture'}


@asynccontextmanager
async def lifespan(application):
    dsn = os.environ.get('PREDICTIQ_TEST_DATABASE_URL', '')
    parsed = urlsplit(dsn)
    if parsed.hostname != '127.0.0.1' or parsed.port != 15439 or parsed.path != '/predictiq_integration':
        raise RuntimeError('Authenticated E2E requires the isolated local test database')
    with TemporaryDirectory(prefix='predictiq-auth-e2e-') as directory:
        database._pool = await asyncpg.create_pool(dsn, min_size=1, max_size=3)
        try:
            assert await database._pool.fetchval('SELECT version_num FROM alembic_version') == '005_role_retry'
            storage_service._backend = LocalStorageBackend(directory)
            ml_service.predict = prediction_fixture
            predictor.get_model_info = lambda: {'model_version': 'authenticated-e2e-fixture'}
            yield
        finally:
            await database._pool.close()
            database._pool = None


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
for router in (auth.router, profile.router, documents.router, estimates.router, export.router, shared.router):
    app.include_router(router, prefix='/api/v1')
app.add_middleware(CORSMiddleware, allow_origins=['http://127.0.0.1:5173'],
                   allow_methods=['GET', 'POST', 'PATCH', 'DELETE'], allow_headers=['Authorization', 'Content-Type'])


@app.get('/api/v1/live')
def live():
    return {'status': 'test'}


@app.get('/api/v1/test/identity')
def identity(user: CurrentUser = Depends(get_current_user)):
    return {'id': user.id, 'role': user.role}


@app.get('/api/v1/test/admin')
def admin(user: CurrentUser = Depends(require_role('admin'))):
    return {'id': user.id}

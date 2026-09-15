import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/auth', workers: 1, timeout: 45_000,
  use: { baseURL: 'http://127.0.0.1:5173' },
  webServer: [
    {
      command: 'npm run dev -- --host 127.0.0.1', url: 'http://127.0.0.1:5173',
      reuseExistingServer: false, timeout: 120_000,
      env: { VITE_AUTH_EMULATOR: 'true', VITE_FIREBASE_PROJECT_ID: 'demo-predictiq',
        VITE_FIREBASE_API_KEY: 'demo-api-key', VITE_FIREBASE_AUTH_DOMAIN: 'demo-predictiq.firebaseapp.com' },
    },
    {
      command: `"${process.env.PREDICTIQ_TEST_PYTHON || (process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : 'python')}" -m uvicorn tests.auth_emulator_server:app --host 127.0.0.1 --port 8000 --no-access-log`,
      cwd: '../backend', url: 'http://127.0.0.1:8000/api/v1/live', reuseExistingServer: false, timeout: 120_000,
    },
  ],
});

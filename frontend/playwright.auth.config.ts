import { defineConfig } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pythonExe = process.env.PREDICTIQ_TEST_PYTHON || (process.platform === 'win32'
  ? path.resolve(__dirname, '../.venv/Scripts/python.exe')
  : 'python');

export default defineConfig({
  testDir: './e2e/auth', workers: 1, timeout: 45_000,
  use: { baseURL: 'http://127.0.0.1:5173' },
  webServer: [
    {
      command: 'npm run dev -- --host 127.0.0.1', url: 'http://127.0.0.1:5173',
      reuseExistingServer: false, timeout: 120_000,
      env: {
        VITE_AUTH_EMULATOR: 'true',
        VITE_FIREBASE_PROJECT_ID: 'demo-predictiq',
        VITE_FIREBASE_API_KEY: 'demo-api-key',
        VITE_FIREBASE_AUTH_DOMAIN: 'demo-predictiq.firebaseapp.com',
        VITE_PROXY_TARGET: 'http://127.0.0.1:8010',
      },
    },
    {
      command: `"${pythonExe}" -m uvicorn tests.auth_emulator_server:app --host 127.0.0.1 --port 8010 --no-access-log`,
      cwd: '../backend', url: 'http://127.0.0.1:8010/api/v1/live', reuseExistingServer: false, timeout: 120_000,
    },
  ],
});

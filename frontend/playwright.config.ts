import { defineConfig, devices } from '@playwright/test';

/**
 * Predictify — Playwright E2E Configuration
 * Runs against the local dev server (frontend:5173 + backend:8000).
 */
export default defineConfig({
  testDir: './e2e',
  testIgnore: '**/auth/**',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  timeout: 30_000,

  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  /* Start dev server before tests if not already running */
  webServer: [
    {
      command: 'npm run dev -- --host 127.0.0.1',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: false,
      timeout: 120_000,
      // UI contract tests must not depend on a developer's private .env or CI's
      // production Firebase configuration. All network interactions are fixtures.
      env: { VITE_FIREBASE_API_KEY: 'demo-api-key', VITE_FIREBASE_PROJECT_ID: 'demo-predictiq',
        VITE_FIREBASE_AUTH_DOMAIN: 'demo-predictiq.firebaseapp.com' },
    },
    {
      command: `"${process.env.PREDICTIQ_TEST_PYTHON || (process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : 'python')}" -m uvicorn tests.browser_server:app --host 127.0.0.1 --port 8000 --no-access-log`,
      cwd: '../backend',
      url: 'http://127.0.0.1:8000/api/v1/live',
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});

import { defineConfig } from '@playwright/test';

// Opt-in only. Uses supplied synthetic identities and the protected staging site.
export default defineConfig({
  testDir: './e2e/live', workers: 1, retries: 0, timeout: 120_000,
  reporter: 'list', outputDir: '../.tools/live-browser-results',
  use: {
    baseURL: 'https://predictiq-preview.vercel.app',
    trace: 'off', screenshot: 'off', video: 'off',
  },
});

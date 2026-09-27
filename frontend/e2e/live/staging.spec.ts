import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

test('live staging sign-in, extraction, honest model failure and sign-out', async ({ page }) => {
  const credentials = JSON.parse(readFileSync('../.tools/live-provider-identities.json', 'utf8'));
  const user = credentials.users[0];
  if (!user.uid.startsWith('predictiq-ops-') || !user.email.endsWith('@example.invalid')) {
    throw new Error('Only synthetic operational identities are allowed');
  }
  // May be the public alias or an expiring provider-generated access link. Never trace it.
  const access = JSON.parse(readFileSync('../.tools/vercel-staging-access.json', 'utf8'));
  const url = new URL(access.url);
  if (url.protocol !== 'https:' || !url.hostname.startsWith('predictiq-preview') ||
      !url.hostname.endsWith('.vercel.app')) throw new Error('Unexpected staging host');
  await page.goto(url.toString());
  const origin = new URL(page.url()).origin;
  await page.goto(origin + '/auth');
  await expect(page.getByRole('status').filter({ hasText: 'Staging' })).toBeVisible();
  await page.getByLabel('Email', { exact: true }).fill(user.email);
  await page.getByLabel('Password', { exact: true }).fill(user.password);
  await page.getByRole('button', { name: 'Sign In', exact: true }).click();
  await expect(page).toHaveURL(/dashboard/, { timeout: 45_000 });
  await page.reload();
  await expect(page.getByRole('button', { name: 'Account options' })).toBeVisible();
  await page.getByRole('navigation', { name: 'Workspace navigation' }).getByRole('link', { name: 'New Estimate' }).click();
  await page.locator('#file-input').setInputFiles({
    name: 'live-browser-acceptance.txt', mimeType: 'text/plain',
    buffer: Buffer.from('Project: Live Browser Acceptance. Build a web application with React and Python. A team of three developers will work for four months using Agile. Users register accounts, manage projects, search tasks, export reports and view dashboards. Integrate email and payment APIs. Synthetic operational fixture; exclude from ML training.'),
  });
  await page.getByRole('button', { name: 'Upload & Continue' }).click();
  await expect(page.getByLabel('Project Name')).toBeVisible({ timeout: 45_000 });
  await page.getByLabel('Project Name').fill('Live Browser Acceptance');
  const analyzed = page.waitForResponse(r => r.url().endsWith('/estimates/analyze') && r.request().method() === 'POST');
  await page.getByRole('button', { name: /generate estimate/i }).click();
  const response = await analyzed;
  expect(response.status()).toBe(503);
  expect((await response.json()).detail).toBe('Prediction service is unavailable');
  await expect(page.getByRole('main').getByRole('alert')).toContainText('Prediction service is unavailable');
  await page.getByRole('button', { name: 'Account options' }).click();
  await page.getByRole('button', { name: 'Sign Out', exact: true }).click();
  await expect(page).toHaveURL(/auth/);
  await page.goto(origin + '/dashboard');
  await expect(page).toHaveURL(/auth/);
});

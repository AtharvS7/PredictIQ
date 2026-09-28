import { test, expect } from '@playwright/test';
import { randomUUID } from 'node:crypto';

test('Firebase sign-in yields a verified API identity and enforces roles', async ({ page, request }) => {
  const email = `e2e-${Date.now()}@example.invalid`;
  const password = randomUUID();
  const created = await request.post('http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:signUp?key=demo-api-key', {
    data: { email, password, returnSecureToken: true },
  });
  expect(created.ok()).toBe(true);
  const { localId } = await created.json();
  await page.route('**/*', route => {
    const host = new URL(route.request().url()).hostname;
    return ['127.0.0.1', 'localhost'].includes(host) ? route.continue() : route.abort();
  });
  await page.goto('/auth');
  await page.getByLabel('Email', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign In', exact: true }).click();
  await expect(page).toHaveURL(/dashboard/);
  const result = await page.evaluate(async () => {
    const modulePath = '/src/lib/firebase.ts';
    const { auth } = await import(modulePath);
    const token = await auth.currentUser.getIdToken();
    const headers = { Authorization: `Bearer ${token}` };
    const identity = await fetch('http://127.0.0.1:8000/api/v1/test/identity', { headers });
    const admin = await fetch('http://127.0.0.1:8000/api/v1/test/admin', { headers });
    return { status: identity.status, identity: await identity.json(), admin: admin.status };
  });
  expect(result).toEqual({ status: 200, identity: { id: localId, role: 'editor' }, admin: 403 });
  await page.getByRole('link', { name: 'Budget Planner', exact: true }).click();
  for (const [label, value] of [['Project name', 'Verified task budget'], ['Task name', 'Build'],
    ['Low hours', '10'], ['Likely hours', '20'], ['High hours', '30'], ['Rate (USD/hour)', '75'], ['Contingency (%)', '10']]) {
    await page.getByLabel(label, { exact: true }).fill(value);
  }
  await page.getByRole('button', { name: 'Calculate and save budget' }).click();
  await expect(page.getByRole('region', { name: 'Saved budget result' }).getByText('$1,650.00')).toBeVisible();
  await page.reload();
  await page.getByRole('button', { name: /Verified task budget/ }).click();
  await expect(page.getByRole('region', { name: 'Saved budget result' }).getByText('$1,650.00')).toBeVisible();
  await page.setViewportSize({ width: 375, height: 812 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  const mobileLinks = await page.locator('.workspace-nav-link').evaluateAll(links => links.map(link => {
    const box = link.getBoundingClientRect(); return { top: box.top, width: box.width, height: box.height };
  }));
  expect(mobileLinks).toHaveLength(5);
  expect(new Set(mobileLinks.map(link => link.top)).size).toBe(1);
  expect(mobileLinks.every(link => link.width >= 44 && link.height >= 44)).toBe(true);
  if (process.env.PREDICTIQ_CAPTURE_UI === '1') {
    await page.screenshot({ path: '../.tools/budget-ui-mobile.png', fullPage: true });
  }
  await page.setViewportSize({ width: 1280, height: 900 });
  if (process.env.PREDICTIQ_CAPTURE_UI === '1') {
    await page.screenshot({ path: '../.tools/budget-ui-desktop.png', fullPage: true });
  }
  expect((await request.get('http://127.0.0.1:8000/api/v1/test/identity', {
    headers: { Authorization: 'Bearer invalid-token' },
  })).status()).toBe(401);
  await page.getByRole('navigation', { name: 'Workspace navigation' }).getByRole('link', { name: 'New Estimate' }).click();
  await page.locator('#file-input').setInputFiles({ name: 'project.txt', mimeType: 'text/plain',
    buffer: Buffer.from('Project: Customer Portal. Build a web application with React and Python. A team of 5 developers will work for 6 months using Agile. Users must register accounts, manage customer records, search products, export reports, and view dashboards. Integrate payment and email APIs.') });
  await page.getByRole('button', { name: 'Upload & Continue' }).click();
  await expect(page.getByLabel('Project Name')).toBeVisible({ timeout: 30_000 });
  await page.getByLabel('Project Name').fill('Authenticated project flow');
  const analyzed = page.waitForResponse(response => response.url().endsWith('/estimates/analyze') && response.request().method() === 'POST');
  await page.getByRole('button', { name: /generate estimate/i }).click();
  const response = await analyzed;
  expect(response.status()).toBe(200);
  const estimate = await response.json();
  expect(estimate.model_version).toBe('authenticated-e2e-fixture');
  expect(estimate.outputs.cost_likely_usd).toBeCloseTo(estimate.outputs.effort_likely_hours * estimate.inputs.hourly_rate_usd, 1);
  await expect(page.getByRole('heading', { name: 'Authenticated project flow' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Authenticated project flow' })).toBeVisible();
  // A second real emulator identity cannot read the first user's persisted result.
  const other = await request.post('http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:signUp?key=demo-api-key', {
    data: { email: `other-${Date.now()}@example.invalid`, password, returnSecureToken: true },
  });
  const otherToken = (await other.json()).idToken;
  expect((await request.get(`http://127.0.0.1:8000/api/v1/estimates/${estimate.estimate_id}`, {
    headers: { Authorization: `Bearer ${otherToken}` },
  })).status()).toBe(404);
  await page.reload();
  await expect(page.getByRole('button', { name: 'Account options' })).toBeVisible();
  await page.getByRole('button', { name: 'Account options' }).click();
  await page.getByRole('button', { name: 'Sign Out', exact: true }).click();
  await expect(page).toHaveURL(/auth/);
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/auth/);
});

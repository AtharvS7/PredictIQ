import { test, expect } from '@playwright/test';

test('Firebase sign-in yields a verified API identity and enforces roles', async ({ page, request }) => {
  const email = `e2e-${Date.now()}@example.invalid`;
  const password = 'Local-test-only-123!';
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
  expect((await request.get('http://127.0.0.1:8000/api/v1/test/identity', {
    headers: { Authorization: 'Bearer invalid-token' },
  })).status()).toBe(401);
  await page.reload();
  await expect(page.getByRole('button', { name: 'Account options' })).toBeVisible();
  await page.getByRole('button', { name: 'Account options' }).click();
  await page.getByRole('button', { name: 'Sign Out', exact: true }).click();
  await expect(page).toHaveURL(/auth/);
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/auth/);
});

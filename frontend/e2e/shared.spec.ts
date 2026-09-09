import { test, expect } from '@playwright/test';

test('shared link opens publicly and shows expired links clearly', async ({ page }) => {
  await page.route('**/api/v1/shared/**', route => route.fulfill({ status: 404, json: { detail: 'Share link is unavailable' } }));
  await page.goto('/share/expired-token');
  await expect(page.getByRole('main').getByRole('alert')).toContainText('expired or is unavailable');
  await expect(page.getByText('Shared estimate · Read only')).toBeVisible();
});

test('password-protected sharing prompts for its password without login', async ({ page }) => {
  await page.route('**/api/v1/shared/**', route => route.fulfill({ status: 401, json: { detail: 'A valid share password is required' } }));
  await page.goto('/share/password-token');
  await expect(page.getByLabel('Share password')).toBeVisible();
  await page.getByLabel('Share password').fill('incorrect');
  await page.getByRole('button', { name: 'Open estimate' }).click();
  await expect(page.getByRole('main').getByRole('alert')).toHaveText('Incorrect password.');
});

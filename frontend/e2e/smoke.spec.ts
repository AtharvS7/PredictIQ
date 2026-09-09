import { test, expect } from '@playwright/test';

/**
 * Predictify — E2E Smoke Tests
 * Basic tests to verify the app loads and key pages are accessible.
 * Run with: npx playwright test
 */

test.describe('Landing Page', () => {
  test('should load and show app name', async ({ page }) => {
    await page.goto('/');
    // Landing page should contain the app name
    await expect(page.locator('body')).toContainText(/Predictify/i);
  });

  test('should have navigation elements', async ({ page }) => {
    await page.goto('/');
    // Should have at least one link or button for navigation
    const navLinks = page.locator('a, button');
    await expect(navLinks.first()).toBeVisible();
  });

  test('should be responsive (mobile viewport)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    // Page should still load without errors
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Auth Page', () => {
  test('should show login form', async ({ page }) => {
    await page.goto('/auth');
    // Auth page should have sign-in elements
    await expect(page.locator('body')).toContainText(/sign|login|auth/i);
    await expect(page.getByRole('textbox', { name: 'Email', exact: true })).toBeVisible();
    const password = page.getByLabel('Password', { exact: true });
    await password.fill('local-test-value');
    await page.getByRole('button', { name: 'Show password' }).click();
    await expect(password).toHaveAttribute('type', 'text');
    await page.getByRole('button', { name: 'Hide password' }).click();
    await expect(password).toHaveAttribute('type', 'password');
  });
});

test.describe('Security Headers', () => {
  test('API should return security headers', async ({ request }) => {
    const response = await request.get('http://localhost:8000/');
    expect(response.headers()['x-frame-options']).toBe('DENY');
    expect(response.headers()['x-content-type-options']).toBe('nosniff');
  });

  test('API readiness rejects unavailable dependencies', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/health');
    expect(response.status()).toBe(503);
    const body = await response.json();
    expect(body.status).toBe('degraded');
  });
});

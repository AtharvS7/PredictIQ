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
  });
});

test.describe('Security Headers', () => {
  test('API should return security headers', async ({ request }) => {
    const response = await request.get('http://localhost:8000/');
    expect(response.headers()['x-frame-options']).toBe('DENY');
    expect(response.headers()['x-content-type-options']).toBe('nosniff');
  });

  test('API health endpoint should return 200', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/health');
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBeDefined();
  });
});

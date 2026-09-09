import { test, expect } from '@playwright/test';

const savedEstimate = {
  estimate_id: '00000000-0000-4000-8000-000000000001', project_name: 'Saved layout fixture',
  created_at: '2026-01-01', version: 1, status: 'complete', model_version: 'test-fixture',
  inputs: { project_type: 'Web App', tech_stack: [], team_size: 2, duration_months: 2, complexity: 'Medium', methodology: 'Agile', hourly_rate_usd: 50 },
  outputs: {
    effort_min_hours: 80, effort_likely_hours: 100, effort_max_hours: 120,
    cost_min_usd: 4000, cost_likely_usd: 5000, cost_max_usd: 6000,
    timeline_min_weeks: 1, timeline_likely_weeks: 2, timeline_max_weeks: 3,
    confidence_pct: 80, risk_score: 42, risk_level: 'High', top_risks: [], phase_breakdown: [],
    model_explanation: 'Synthetic layout fixture', benchmark_comparison: 'Synthetic layout fixture',
  },
};

// Synthetic identity/API responses: layout checks, not Firebase authentication.
test('workspace responsive navigation and keyboard controls', async ({ page }) => {
  await page.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (!['127.0.0.1', 'localhost'].includes(url.hostname)) return route.abort();
    if (url.pathname.startsWith('/api/')) {
      if (url.pathname.endsWith(savedEstimate.estimate_id)) return route.fulfill({ json: savedEstimate });
      if (url.pathname.endsWith('/estimates/manual')) {
        return route.fulfill({ status: 503, json: { detail: 'Prediction unavailable' } });
      }
      return route.fulfill({ json: { estimates: [], total: 0, page: 1, per_page: 20 } });
    }
    return route.continue();
  });
  await page.goto('/auth');
  await expect(page.getByRole('heading', { name: /welcome back/i })).toBeVisible();
  await page.evaluate(async () => {
    const modulePath = '/src/store/authStore.ts';
    const { useAuthStore } = await import(modulePath);
    const user = { uid: 'layout-test', email: 'layout@example.invalid' };
    useAuthStore.setState({ user, session: { user }, loading: false, initialized: true, role: 'editor' });
    history.pushState({}, '', '/dashboard');
    window.dispatchEvent(new PopStateEvent('popstate'));
  });
  const nav = page.getByRole('navigation', { name: 'Workspace navigation' });
  await expect(nav).toBeVisible();
  // Shared text tokens must remain readable on every workspace surface.
  for (const theme of ['light', 'dark']) {
    const ratios = await page.evaluate(themeName => {
      document.documentElement.dataset.theme = themeName;
      const style = getComputedStyle(document.documentElement);
      const luminance = (hex: string) => {
        const values = hex.trim().replace('#', '').match(/../g)!.map(value => {
          const channel = parseInt(value, 16) / 255;
          return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
        });
        return values[0] * 0.2126 + values[1] * 0.7152 + values[2] * 0.0722;
      };
      return ['--text-primary', '--text-secondary', '--text-tertiary'].flatMap(text =>
        ['--bg-primary', '--bg-surface', '--bg-elevated'].map(background => {
          const a = luminance(style.getPropertyValue(text));
          const b = luminance(style.getPropertyValue(background));
          return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        }));
    }, theme);
    for (const ratio of ratios) expect(ratio).toBeGreaterThanOrEqual(4.5);
  }
  for (const width of [375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await expect(nav.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('aria-current', 'page');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const box = await nav.getByRole('link', { name: 'New Estimate' }).boundingBox();
    expect(box!.height).toBeGreaterThanOrEqual(44);
    if (width === 375) {
      await expect(nav.getByRole('button', { name: 'Collapse sidebar' })).toBeHidden();
      expect((await nav.boundingBox())!.y).toBeGreaterThan(700);
    }
  }
  await page.getByRole('button', { name: 'Collapse sidebar' }).click();
  await expect(nav.getByRole('link', { name: 'Settings' })).toBeVisible();
  const account = page.getByRole('button', { name: 'Account options' });
  await account.click();
  await expect(account).toHaveAttribute('aria-expanded', 'true');
  await page.keyboard.press('Escape');
  await expect(account).toBeFocused();
  await expect(account).toHaveAttribute('aria-expanded', 'false');
  await page.getByRole('button', { name: 'Toggle appearance' }).click();
  expect(await page.evaluate(() => localStorage.getItem('Predictify-theme'))).toMatch(/^(light|dark)$/);
  await page.screenshot({ path: 'test-results/workspace-desktop.png', fullPage: true });
  await page.setViewportSize({ width: 375, height: 812 });
  await page.screenshot({ path: 'test-results/workspace-mobile.png', fullPage: true });
  await nav.getByRole('link', { name: 'New Estimate' }).click();
  await expect(page.getByRole('button', { name: 'Choose document' })).toBeVisible();
  await page.getByRole('button', { name: /manual/i }).click();
  await expect(page.getByRole('main').getByRole('heading', { level: 2 })).toBeFocused();
  await page.getByLabel('Project Name').fill('Preserved project');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.getByRole('button', { name: /generate estimate/i }).click();
  await expect(page.getByRole('main').getByRole('alert')).toContainText('Prediction service is unavailable');
  await expect(page.getByRole('main').getByRole('heading', { level: 2 })).toBeFocused();
  await expect(page.getByLabel('Project Name')).toHaveValue('Preserved project');
  await nav.getByRole('link', { name: 'Settings', exact: true }).click();
  await page.getByLabel('Hourly Rate (USD)').fill('0');
  await page.getByRole('button', { name: 'Save Changes' }).click();
  await expect(page.getByRole('main').getByRole('alert')).toContainText('between 10 and 500 USD');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.evaluate(id => {
    history.pushState({}, '', `/estimate/${id}/results`);
    window.dispatchEvent(new PopStateEvent('popstate'));
  }, savedEstimate.estimate_id);
  await expect(page.getByRole('heading', { name: 'Saved layout fixture' })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: 'test-results/results-mobile.png', fullPage: true });
});

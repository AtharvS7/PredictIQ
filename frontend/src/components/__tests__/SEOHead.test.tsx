/**
 * Predictify — SEOHead Component Tests
 */
import { describe, it, expect, afterEach } from 'vitest';
import { render, cleanup } from '@testing-library/react';
import SEOHead from '../../components/shared/SEOHead';

describe('SEOHead', () => {
  afterEach(() => {
    cleanup();
    // Reset document title
    document.title = '';
    // Remove injected meta tags
    document.querySelectorAll('meta[property^="og:"]').forEach(el => el.remove());
    document.querySelector('meta[name="description"]')?.remove();
  });

  it('sets document title with Predictify suffix', () => {
    render(<SEOHead title="Dashboard" />);
    expect(document.title).toBe('Dashboard | Predictify');
  });

  it('sets meta description when provided', () => {
    render(<SEOHead title="Test" description="A test page" />);
    const meta = document.querySelector('meta[name="description"]');
    expect(meta).not.toBeNull();
    expect(meta?.getAttribute('content')).toBe('A test page');
  });

  it('sets Open Graph title tag', () => {
    render(<SEOHead title="Estimates" />);
    const ogTitle = document.querySelector('meta[property="og:title"]');
    expect(ogTitle).not.toBeNull();
    expect(ogTitle?.getAttribute('content')).toBe('Estimates | Predictify');
  });

  it('sets og:site_name to Predictify', () => {
    render(<SEOHead title="Test" />);
    const ogSiteName = document.querySelector('meta[property="og:site_name"]');
    expect(ogSiteName?.getAttribute('content')).toBe('Predictify');
  });

  it('resets title on unmount', () => {
    const { unmount } = render(<SEOHead title="Custom" />);
    expect(document.title).toBe('Custom | Predictify');
    unmount();
    expect(document.title).toBe('Predictify — Smart Project Estimation');
  });

  it('renders null (no visible UI)', () => {
    const { container } = render(<SEOHead title="Test" />);
    expect(container.innerHTML).toBe('');
  });
});

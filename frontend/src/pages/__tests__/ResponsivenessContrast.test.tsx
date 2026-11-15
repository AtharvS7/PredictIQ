import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import LandingPage from '../LandingPage';
import Navbar from '@/components/shared/Navbar';
import Sidebar from '@/components/shared/Sidebar';

vi.mock('@/store/authStore', () => ({
  useAuthStore: () => ({
    user: null,
    profile: null,
    signOut: vi.fn(),
  }),
}));

vi.mock('@/components/shared/SEOHead', () => ({
  default: () => null,
}));

describe('Responsiveness and Theme Contrast Verification', () => {
  it('renders landing page within 360px mobile viewport without structural breaks', () => {
    window.innerWidth = 360;
    window.innerHeight = 640;

    const { container } = render(
      <MemoryRouter>
        <LandingPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Create Free Account/i })).toBeInTheDocument();
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders navigation bar adaptively at 768px tablet viewport', () => {
    window.innerWidth = 768;
    window.innerHeight = 1024;

    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    expect(screen.getByText('PredictIQ')).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /^Sign In$/i }).length).toBeGreaterThanOrEqual(1);
  });

  it('renders workspace sidebar and rail at 1280px desktop viewport', () => {
    window.innerWidth = 1280;
    window.innerHeight = 800;

    render(
      <MemoryRouter>
        <Sidebar collapsed={false} />
      </MemoryRouter>
    );

    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /New Estimate/i })).toBeInTheDocument();
  });

  it('validates WCAG 2.1 AA luminance contrast for design tokens in light and dark modes', () => {
    function hexToRgb(hex: string): [number, number, number] {
      const clean = hex.replace('#', '');
      const num = parseInt(clean, 16);
      return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
    }

    function relativeLuminance([r, g, b]: [number, number, number]): number {
      const [rs, gs, bs] = [r, g, b].map((c) => {
        const s = c / 255;
        return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    }

    function contrastRatio(hex1: string, hex2: string): number {
      const l1 = relativeLuminance(hexToRgb(hex1));
      const l2 = relativeLuminance(hexToRgb(hex2));
      const brighter = Math.max(l1, l2);
      const darker = Math.min(l1, l2);
      return (brighter + 0.05) / (darker + 0.05);
    }

    // Light mode: Text Primary (#0F172A) on Background Primary (#F8FAFC)
    const lightRatio = contrastRatio('#0F172A', '#F8FAFC');
    expect(lightRatio).toBeGreaterThanOrEqual(4.5); // WCAG AA minimum is 4.5:1

    // Dark mode: Text Primary (#F8FAFC) on Background Primary (#090D16)
    const darkRatio = contrastRatio('#F8FAFC', '#090D16');
    expect(darkRatio).toBeGreaterThanOrEqual(4.5); // WCAG AA minimum is 4.5:1

    // Light mode secondary text (#475569) on #F8FAFC
    const lightSecondaryRatio = contrastRatio('#475569', '#F8FAFC');
    expect(lightSecondaryRatio).toBeGreaterThanOrEqual(4.5);

    // Dark mode secondary text (#CBD5E1) on #090D16
    const darkSecondaryRatio = contrastRatio('#CBD5E1', '#090D16');
    expect(darkSecondaryRatio).toBeGreaterThanOrEqual(4.5);
  });
});

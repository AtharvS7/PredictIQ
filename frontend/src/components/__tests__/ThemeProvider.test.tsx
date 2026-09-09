import { act, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ThemeProvider, { useTheme } from '../ThemeProvider';

function Control() {
  const { theme, resolvedTheme, setTheme } = useTheme();
  return <><span>{theme}</span><output aria-label="Resolved theme">{resolvedTheme}</output><button onClick={() => setTheme('light')}>Light</button></>;
}

describe('Shared appearance preference', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() })));
  });
  afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });
  it('follows system changes and cleans up its listener', () => {
    let listener: (() => void) | undefined;
    const preference = { matches: true, addEventListener: vi.fn((_name, callback) => { listener = callback; }), removeEventListener: vi.fn() };
    vi.spyOn(window, 'matchMedia').mockReturnValue(preference as unknown as MediaQueryList);
    const { unmount } = render(<ThemeProvider><Control /></ThemeProvider>);
    expect(document.documentElement.dataset.theme).toBe('dark');
    expect(screen.getByLabelText('Resolved theme')).toHaveTextContent('dark');
    act(() => { preference.matches = false; listener?.(); });
    expect(document.documentElement.dataset.theme).toBe('light');
    expect(screen.getByLabelText('Resolved theme')).toHaveTextContent('light');
    unmount();
    expect(preference.removeEventListener).toHaveBeenCalledWith('change', expect.any(Function));
    vi.restoreAllMocks();
  });

  it('persists an explicit choice in the application setting', () => {
    localStorage.setItem('Predictify-theme', 'dark');
    render(<ThemeProvider><Control /></ThemeProvider>);
    fireEvent.click(screen.getByRole('button', { name: 'Light' }));
    expect(localStorage.getItem('Predictify-theme')).toBe('light');
    expect(document.documentElement.dataset.theme).toBe('light');
  });
});

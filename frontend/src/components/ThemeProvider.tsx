import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

interface ThemeContextType { theme: string; resolvedTheme: string; setTheme: (theme: string) => void; }
export const ThemeContext = createContext<ThemeContextType>({ theme: 'system', resolvedTheme: 'light', setTheme: () => {} });
export const useTheme = () => useContext(ThemeContext);

export default function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState(() => {
    const saved = localStorage.getItem('Predictify-theme');
    return saved === 'dark' || saved === 'light' ? saved : 'system';
  });
  const [resolvedTheme, setResolvedTheme] = useState(() => theme === 'system'
    ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : theme);
  const setTheme = (value: string) => {
    if (['dark', 'light', 'system'].includes(value)) setThemeState(value);
  };
  useEffect(() => {
    const preference = window.matchMedia('(prefers-color-scheme: dark)');
    const apply = () => {
      const resolved = theme === 'system' ? (preference.matches ? 'dark' : 'light') : theme;
      document.documentElement.dataset.theme = resolved;
      setResolvedTheme(resolved);
    };
    apply();
    localStorage.setItem('Predictify-theme', theme);
    preference.addEventListener('change', apply);
    return () => preference.removeEventListener('change', apply);
  }, [theme]);
  return <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>{children}</ThemeContext.Provider>;
}

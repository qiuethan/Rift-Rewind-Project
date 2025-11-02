import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import {
  RegionTheme,
  getRandomRegionTheme,
  getThemeById,
  THEME_STORAGE_KEY,
} from '@/config/runeterraThemes';

interface ThemeContextType {
  theme: RegionTheme;
  setTheme: (themeId: string) => void;
  refreshTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<RegionTheme>(() => {
    // Try to get theme from sessionStorage first
    const storedThemeId = sessionStorage.getItem(THEME_STORAGE_KEY);
    if (storedThemeId) {
      return getThemeById(storedThemeId);
    }
    // Otherwise, select random theme
    const randomTheme = getRandomRegionTheme();
    sessionStorage.setItem(THEME_STORAGE_KEY, randomTheme.id);
    return randomTheme;
  });

  // Apply theme to CSS variables whenever theme changes
  useEffect(() => {
    applyThemeToDOM(theme);
  }, [theme]);

  const setTheme = (themeId: string) => {
    const newTheme = getThemeById(themeId);
    setThemeState(newTheme);
    sessionStorage.setItem(THEME_STORAGE_KEY, newTheme.id);
  };

  const refreshTheme = () => {
    const newTheme = getRandomRegionTheme();
    setThemeState(newTheme);
    sessionStorage.setItem(THEME_STORAGE_KEY, newTheme.id);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, refreshTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

/**
 * Apply theme colors to CSS custom properties
 */
function applyThemeToDOM(theme: RegionTheme) {
  const root = document.documentElement;

  // Apply palette colors
  root.style.setProperty('--region-primary', theme.palette.primary);
  root.style.setProperty('--region-secondary', theme.palette.secondary);
  root.style.setProperty('--region-accent', theme.palette.accent);
  root.style.setProperty('--region-text', theme.palette.text);
  root.style.setProperty('--region-text-secondary', theme.palette.textSecondary);
  root.style.setProperty('--region-text-dim', theme.palette.textDim);
  root.style.setProperty('--region-bg-gradient', theme.palette.bgGradient);
  root.style.setProperty('--region-panel', theme.palette.panel);
  root.style.setProperty('--region-panel-border', theme.palette.panelBorder);
  root.style.setProperty('--region-panel-hover', theme.palette.panelHover);
  root.style.setProperty('--region-danger', theme.palette.danger);
  root.style.setProperty('--region-success', theme.palette.success);
  root.style.setProperty('--region-warning', theme.palette.warning);

  // Apply shadows
  root.style.setProperty('--region-shadow-primary', theme.shadows.primary);
  root.style.setProperty('--region-shadow-secondary', theme.shadows.secondary);
  root.style.setProperty('--region-shadow-glow', theme.shadows.glow);

  // Apply background image
  root.style.setProperty('--region-bg-image', `url('${theme.images.background}')`);
  root.style.setProperty('--region-pattern', `url('${theme.images.pattern}')`);

  // Update body background
  document.body.style.background = theme.palette.secondary;
  document.body.style.backgroundImage = theme.palette.bgGradient;

  // Add data attribute for theme-specific styling
  root.setAttribute('data-region-theme', theme.id);
}

/**
 * RUNETERRA REGION THEMES
 * 
 * Dynamic visual identity system that randomly applies one of 10 League of Legends
 * region themes on each app load. Maintains identical UX while changing aesthetics.
 */

export interface RegionTheme {
  id: string;
  name: string;
  palette: {
    primary: string;
    secondary: string;
    accent: string;
    text: string;
    textSecondary: string;
    textDim: string;
    bgGradient: string;
    panel: string;
    panelBorder: string;
    panelHover: string;
    danger: string;
    success: string;
    warning: string;
  };
  shadows: {
    primary: string;
    secondary: string;
    glow: string;
  };
  images: {
    hero: string;
    background: string;
    pattern: string;
    decorative?: string;
  };
  tagline: string;
  particles?: string;
  fonts?: {
    heading?: string;
    body?: string;
  };
}

export const RUNETERRA_THEMES: Record<string, RegionTheme> = {
  piltover: {
    id: 'piltover',
    name: 'Piltover & Zaun',
    palette: {
      primary: '#F5C96A',
      secondary: '#243A52',
      accent: '#55F2CE',
      text: '#E9E6E1',
      textSecondary: '#B8B5B0',
      textDim: '#8A8780',
      bgGradient: 'linear-gradient(160deg, #0D1117 0%, #1A2738 90%)',
      panel: 'rgba(245, 201, 106, 0.08)',
      panelBorder: 'rgba(245, 201, 106, 0.35)',
      panelHover: 'rgba(245, 201, 106, 0.12)',
      danger: '#FF4D4D',
      success: '#55F2CE',
      warning: '#F5C96A',
    },
    shadows: {
      primary: '0 0 25px rgba(245, 201, 106, 0.25)',
      secondary: '0 0 40px rgba(85, 242, 206, 0.3)',
      glow: 'inset 0 0 20px rgba(245, 201, 106, 0.1)',
    },
    images: {
      hero: '/img/regions/piltover-hero.jpg',
      background: '/img/regions/piltover-bg.jpg',
      pattern: '/img/regions/piltover-pattern.svg',
      decorative: '/img/regions/piltover-hextech.svg',
    },
    tagline: 'Innovation through precision.',
    particles: '/particles/hextech-blue.webm',
  },

  ionia: {
    id: 'ionia',
    name: 'Ionia',
    palette: {
      primary: '#E9A7FF',
      secondary: '#0A0C14',
      accent: '#6BF7A7',
      text: '#F3E8FF',
      textSecondary: '#C8B8D5',
      textDim: '#9888A5',
      bgGradient: 'linear-gradient(160deg, #0A0C14 0%, #221B33 90%)',
      panel: 'rgba(233, 167, 255, 0.08)',
      panelBorder: 'rgba(233, 167, 255, 0.35)',
      panelHover: 'rgba(233, 167, 255, 0.12)',
      danger: '#FF6B9D',
      success: '#6BF7A7',
      warning: '#FFB347',
    },
    shadows: {
      primary: '0 0 25px rgba(233, 167, 255, 0.3)',
      secondary: '0 0 40px rgba(107, 247, 167, 0.25)',
      glow: 'inset 0 0 20px rgba(233, 167, 255, 0.1)',
    },
    images: {
      hero: '/img/regions/ionia-hero.jpg',
      background: '/img/regions/ionia-bg.jpg',
      pattern: '/img/regions/ionia-brush.svg',
      decorative: '/img/regions/ionia-spirit.svg',
    },
    tagline: 'Harmony through balance.',
    particles: '/particles/ionia-petals.webm',
  },

  demacia: {
    id: 'demacia',
    name: 'Demacia',
    palette: {
      primary: '#F5F6FA',
      secondary: '#152136',
      accent: '#C7D9FF',
      text: '#EAEFFF',
      textSecondary: '#B8C5E0',
      textDim: '#8895B0',
      bgGradient: 'linear-gradient(180deg, #0E1621 0%, #0A0F15 90%)',
      panel: 'rgba(245, 246, 250, 0.08)',
      panelBorder: 'rgba(199, 217, 255, 0.35)',
      panelHover: 'rgba(245, 246, 250, 0.12)',
      danger: '#FF5757',
      success: '#A7E7FF',
      warning: '#FFD966',
    },
    shadows: {
      primary: '0 0 25px rgba(199, 217, 255, 0.3)',
      secondary: '0 0 40px rgba(245, 246, 250, 0.25)',
      glow: 'inset 0 0 20px rgba(199, 217, 255, 0.1)',
    },
    images: {
      hero: '/img/regions/demacia-hero.jpg',
      background: '/img/regions/demacia-bg.jpg',
      pattern: '/img/regions/demacia-chevron.svg',
      decorative: '/img/regions/demacia-wings.svg',
    },
    tagline: 'Honor forged in light.',
    particles: '/particles/demacia-light.webm',
  },

  noxus: {
    id: 'noxus',
    name: 'Noxus',
    palette: {
      primary: '#F84848',
      secondary: '#140406',
      accent: '#B19D68',
      text: '#FFE9E9',
      textSecondary: '#D5B8B8',
      textDim: '#A58888',
      bgGradient: 'radial-gradient(circle, #140406 0%, #010101 70%)',
      panel: 'rgba(248, 72, 72, 0.08)',
      panelBorder: 'rgba(248, 72, 72, 0.35)',
      panelHover: 'rgba(248, 72, 72, 0.12)',
      danger: '#FF3333',
      success: '#B19D68',
      warning: '#FF8C42',
    },
    shadows: {
      primary: '0 0 25px rgba(248, 72, 72, 0.35)',
      secondary: '0 0 40px rgba(177, 157, 104, 0.25)',
      glow: 'inset 0 0 20px rgba(248, 72, 72, 0.1)',
    },
    images: {
      hero: '/img/regions/noxus-hero.jpg',
      background: '/img/regions/noxus-bg.jpg',
      pattern: '/img/regions/noxus-stripes.svg',
      decorative: '/img/regions/noxus-axe.svg',
    },
    tagline: 'Strength above all.',
    particles: '/particles/noxus-embers.webm',
  },

  freljord: {
    id: 'freljord',
    name: 'Freljord',
    palette: {
      primary: '#E0FBFF',
      secondary: '#071017',
      accent: '#5CD6FF',
      text: '#E9FAFF',
      textSecondary: '#B8D5E0',
      textDim: '#88A5B0',
      bgGradient: 'linear-gradient(200deg, #071017 0%, #12374C 90%)',
      panel: 'rgba(224, 251, 255, 0.08)',
      panelBorder: 'rgba(92, 214, 255, 0.35)',
      panelHover: 'rgba(224, 251, 255, 0.12)',
      danger: '#FF6B9D',
      success: '#5CD6FF',
      warning: '#FFB84D',
    },
    shadows: {
      primary: '0 0 25px rgba(92, 214, 255, 0.3)',
      secondary: '0 0 40px rgba(224, 251, 255, 0.25)',
      glow: 'inset 0 0 20px rgba(92, 214, 255, 0.1)',
    },
    images: {
      hero: '/img/regions/freljord-hero.jpg',
      background: '/img/regions/freljord-bg.jpg',
      pattern: '/img/regions/freljord-crystal.svg',
      decorative: '/img/regions/freljord-ice.svg',
    },
    tagline: 'Endure the cold. Rise anew.',
    particles: '/particles/freljord-snow.webm',
  },

  shadowisles: {
    id: 'shadowisles',
    name: 'Shadow Isles',
    palette: {
      primary: '#35FFDA',
      secondary: '#020607',
      accent: '#00F0A8',
      text: '#CFFFEF',
      textSecondary: '#9DD5C0',
      textDim: '#6DA590',
      bgGradient: 'radial-gradient(circle, #020607 0%, #020716 70%)',
      panel: 'rgba(53, 255, 218, 0.08)',
      panelBorder: 'rgba(53, 255, 218, 0.35)',
      panelHover: 'rgba(53, 255, 218, 0.12)',
      danger: '#00F0A8',
      success: '#35FFDA',
      warning: '#7DFFB3',
    },
    shadows: {
      primary: '0 0 25px rgba(53, 255, 218, 0.35)',
      secondary: '0 0 40px rgba(0, 240, 168, 0.3)',
      glow: 'inset 0 0 20px rgba(53, 255, 218, 0.1)',
    },
    images: {
      hero: '/img/regions/shadowisles-hero.jpg',
      background: '/img/regions/shadowisles-bg.jpg',
      pattern: '/img/regions/shadow-mist.svg',
      decorative: '/img/regions/shadow-chains.svg',
    },
    tagline: 'Even death serves a purpose.',
    particles: '/particles/shadowisles-mist.webm',
  },

  shurima: {
    id: 'shurima',
    name: 'Shurima',
    palette: {
      primary: '#F4D03F',
      secondary: '#1A0F05',
      accent: '#E67E22',
      text: '#FFF4DC',
      textSecondary: '#D5C5A8',
      textDim: '#A59578',
      bgGradient: 'linear-gradient(180deg, #1A0F05 0%, #2C1810 90%)',
      panel: 'rgba(244, 208, 63, 0.08)',
      panelBorder: 'rgba(244, 208, 63, 0.35)',
      panelHover: 'rgba(244, 208, 63, 0.12)',
      danger: '#E74C3C',
      success: '#F4D03F',
      warning: '#E67E22',
    },
    shadows: {
      primary: '0 0 25px rgba(244, 208, 63, 0.3)',
      secondary: '0 0 40px rgba(230, 126, 34, 0.25)',
      glow: 'inset 0 0 20px rgba(244, 208, 63, 0.1)',
    },
    images: {
      hero: '/img/regions/shurima-hero.jpg',
      background: '/img/regions/shurima-bg.jpg',
      pattern: '/img/regions/shurima-sand.svg',
      decorative: '/img/regions/shurima-sun.svg',
    },
    tagline: 'The desert remembers all.',
    particles: '/particles/shurima-sand.webm',
  },

  targon: {
    id: 'targon',
    name: 'Targon',
    palette: {
      primary: '#A78BFA',
      secondary: '#0A0514',
      accent: '#FCD34D',
      text: '#F3E8FF',
      textSecondary: '#C8B8D5',
      textDim: '#9888A5',
      bgGradient: 'linear-gradient(180deg, #0A0514 0%, #1E1033 90%)',
      panel: 'rgba(167, 139, 250, 0.08)',
      panelBorder: 'rgba(167, 139, 250, 0.35)',
      panelHover: 'rgba(167, 139, 250, 0.12)',
      danger: '#F87171',
      success: '#FCD34D',
      warning: '#FBBF24',
    },
    shadows: {
      primary: '0 0 25px rgba(167, 139, 250, 0.3)',
      secondary: '0 0 40px rgba(252, 211, 77, 0.25)',
      glow: 'inset 0 0 20px rgba(167, 139, 250, 0.1)',
    },
    images: {
      hero: '/img/regions/targon-hero.jpg',
      background: '/img/regions/targon-bg.jpg',
      pattern: '/img/regions/targon-stars.svg',
      decorative: '/img/regions/targon-constellation.svg',
    },
    tagline: 'Ascend beyond mortal limits.',
    particles: '/particles/targon-stars.webm',
  },

  bilgewater: {
    id: 'bilgewater',
    name: 'Bilgewater',
    palette: {
      primary: '#F97316',
      secondary: '#0C1821',
      accent: '#22D3EE',
      text: '#FFF7ED',
      textSecondary: '#D5C5B8',
      textDim: '#A59588',
      bgGradient: 'linear-gradient(160deg, #0C1821 0%, #1E3A4C 90%)',
      panel: 'rgba(249, 115, 22, 0.08)',
      panelBorder: 'rgba(249, 115, 22, 0.35)',
      panelHover: 'rgba(249, 115, 22, 0.12)',
      danger: '#DC2626',
      success: '#22D3EE',
      warning: '#F59E0B',
    },
    shadows: {
      primary: '0 0 25px rgba(249, 115, 22, 0.3)',
      secondary: '0 0 40px rgba(34, 211, 238, 0.25)',
      glow: 'inset 0 0 20px rgba(249, 115, 22, 0.1)',
    },
    images: {
      hero: '/img/regions/bilgewater-hero.jpg',
      background: '/img/regions/bilgewater-bg.jpg',
      pattern: '/img/regions/bilgewater-waves.svg',
      decorative: '/img/regions/bilgewater-anchor.svg',
    },
    tagline: 'Fortune favors the bold.',
    particles: '/particles/bilgewater-water.webm',
  },

  ixtal: {
    id: 'ixtal',
    name: 'Ixtal',
    palette: {
      primary: '#10B981',
      secondary: '#052E16',
      accent: '#FBBF24',
      text: '#ECFDF5',
      textSecondary: '#BBD5C8',
      textDim: '#8AA598',
      bgGradient: 'linear-gradient(160deg, #052E16 0%, #064E3B 90%)',
      panel: 'rgba(16, 185, 129, 0.08)',
      panelBorder: 'rgba(16, 185, 129, 0.35)',
      panelHover: 'rgba(16, 185, 129, 0.12)',
      danger: '#EF4444',
      success: '#10B981',
      warning: '#FBBF24',
    },
    shadows: {
      primary: '0 0 25px rgba(16, 185, 129, 0.3)',
      secondary: '0 0 40px rgba(251, 191, 36, 0.25)',
      glow: 'inset 0 0 20px rgba(16, 185, 129, 0.1)',
    },
    images: {
      hero: '/img/regions/ixtal-hero.jpg',
      background: '/img/regions/ixtal-bg.jpg',
      pattern: '/img/regions/ixtal-jungle.svg',
      decorative: '/img/regions/ixtal-elemental.svg',
    },
    tagline: 'Nature reclaims all.',
    particles: '/particles/ixtal-leaves.webm',
  },
};

/**
 * Get a random region theme
 */
export function getRandomRegionTheme(): RegionTheme {
  const themeKeys = Object.keys(RUNETERRA_THEMES);
  const randomKey = themeKeys[Math.floor(Math.random() * themeKeys.length)];
  return RUNETERRA_THEMES[randomKey];
}

/**
 * Get theme by ID with fallback
 */
export function getThemeById(id: string): RegionTheme {
  return RUNETERRA_THEMES[id] || RUNETERRA_THEMES.piltover;
}

/**
 * Get all available theme IDs
 */
export function getAllThemeIds(): string[] {
  return Object.keys(RUNETERRA_THEMES);
}

/**
 * Session storage key for persisting theme across page navigations
 */
export const THEME_STORAGE_KEY = 'runeterra_current_theme';

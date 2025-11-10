import { useEffect, useRef, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartConfiguration,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';
import styles from './MatchAnalysisChart.module.css';
import { useTheme } from '@/contexts';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface MatchAnalysisChartProps {
  chartConfig: any; // Chart.js configuration from backend
  title?: string;
  skipThemeColors?: boolean; // Skip theme color application if colors are pre-set
  height?: number; // Custom height override
  enableLegendClick?: boolean; // Enable legend click to hide/show datasets (default: false)
}

export default function MatchAnalysisChart({ chartConfig, title, skipThemeColors = false, height, enableLegendClick = false }: MatchAnalysisChartProps) {
  const chartRef = useRef<ChartJS>(null);
  const { theme } = useTheme(); // Get current theme to trigger re-render on change
  const [chartKey, setChartKey] = useState(0);

  useEffect(() => {
    // Force chart re-render when theme changes
    setChartKey(prev => prev + 1);
  }, [theme]);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, []);

  if (!chartConfig || !chartConfig.type || !chartConfig.data) {
    return (
      <div className={styles.noChart}>
        <p>Chart configuration not available</p>
      </div>
    );
  }

  // Check if this is a horizontal bar chart
  const isHorizontal = chartConfig.options?.indexAxis === 'y';
  
  // Get dynamic theme colors from CSS variables (set by ThemeContext)
  const getThemeColor = (varName: string) => {
    return getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
  };
  
  // Theme colors from active Runeterra region theme
  const themeColors = {
    primary: getThemeColor('--region-primary'),
    accent: getThemeColor('--region-accent'),
    secondary: getThemeColor('--region-secondary'),
  };
  
  // Generate color palettes for teams with varied hues, not just shades
  const generateTeamPalette = (baseColor: string, count: number = 5) => {
    // Parse hex color
    const hex = baseColor.replace('#', '');
    let r = parseInt(hex.substr(0, 2), 16) / 255;
    let g = parseInt(hex.substr(2, 2), 16) / 255;
    let b = parseInt(hex.substr(4, 2), 16) / 255;
    
    // Convert to HSL
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0, l = (max + min) / 2;
    
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
        case g: h = ((b - r) / d + 2) / 6; break;
        case b: h = ((r - g) / d + 4) / 6; break;
      }
    }
    
    // Generate varied colors by shifting hue and adjusting lightness
    return Array.from({ length: count }, (_, i) => {
      const hueShift = (i * 0.08) % 1; // Shift hue for variation
      const newH = (h + hueShift) % 1;
      const newL = Math.max(0.3, Math.min(0.7, l + (i % 2 === 0 ? 0.1 : -0.1))); // Alternate lighter/darker
      
      // Convert back to RGB
      const hue2rgb = (p: number, q: number, t: number) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1/6) return p + (q - p) * 6 * t;
        if (t < 1/2) return q;
        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
        return p;
      };
      
      let r2, g2, b2;
      if (s === 0) {
        r2 = g2 = b2 = newL;
      } else {
        const q = newL < 0.5 ? newL * (1 + s) : newL + s - newL * s;
        const p = 2 * newL - q;
        r2 = hue2rgb(p, q, newH + 1/3);
        g2 = hue2rgb(p, q, newH);
        b2 = hue2rgb(p, q, newH - 1/3);
      }
      
      return `rgb(${Math.round(r2 * 255)}, ${Math.round(g2 * 255)}, ${Math.round(b2 * 255)})`;
    });
  };
  
  // Create harmonious color scheme with better separation
  const adjustColor = (hex: string, hueShift: number, satAdjust: number, lightAdjust: number) => {
    // Convert hex to RGB
    const num = parseInt(hex.replace('#', ''), 16);
    let r = (num >> 16) & 0xff;
    let g = (num >> 8) & 0xff;
    let b = num & 0xff;
    
    // Convert to HSL for better color manipulation
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0, l = (max + min) / 2;
    
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
        case g: h = ((b - r) / d + 2) / 6; break;
        case b: h = ((r - g) / d + 4) / 6; break;
      }
    }
    
    // Apply adjustments
    h = (h + hueShift) % 1;
    s = Math.max(0, Math.min(1, s + satAdjust));
    l = Math.max(0, Math.min(1, l + lightAdjust));
    
    // Convert back to RGB
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };
    
    let r2, g2, b2;
    if (s === 0) {
      r2 = g2 = b2 = l;
    } else {
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r2 = hue2rgb(p, q, h + 1/3);
      g2 = hue2rgb(p, q, h);
      b2 = hue2rgb(p, q, h - 1/3);
    }
    
    return `rgb(${Math.round(r2 * 255)}, ${Math.round(g2 * 255)}, ${Math.round(b2 * 255)})`;
  };
  
  // EPS colors: create distinct variations with better separation
  const epsColors = {
    combat: themeColors.primary,                           // Primary color (full saturation)
    economic: adjustColor(themeColors.primary, 0.08, -0.15, 0.15), // Shift hue, desaturate, lighten
    objective: themeColors.accent,                         // Accent color (maximum contrast)
  };
  
  const teamPalettes = {
    team100: generateTeamPalette(themeColors.accent, 5),   // Use accent color for team 100
    team200: generateTeamPalette(themeColors.primary, 5),  // Use primary color for team 200
  };

  // Apply theme colors to datasets (skip if colors are already set by filtering)
  const themedData = { ...chartConfig.data };
  if (themedData.datasets) {
    themedData.datasets = themedData.datasets.map((dataset: any, index: number) => {
      const newDataset = { ...dataset };
      
      // Clean up labels - remove empty parentheses for ARAM games
      if (newDataset.label) {
        newDataset.label = newDataset.label.replace(/\s*\(\s*\)/g, '').trim();
      }
      
      // Add smooth curves for line charts
      if (chartConfig.type === 'line') {
        newDataset.tension = 0.4;
      }
      
      // Skip theme color application if filtering is active
      if (skipThemeColors) {
        return newDataset;
      }
      
      // For EPS breakdown (stacked bar chart)
      if (isHorizontal && chartConfig.data.datasets.length === 3) {
        if (dataset.label?.includes('Combat')) {
          newDataset.backgroundColor = epsColors.combat;
        } else if (dataset.label?.includes('Economic')) {
          newDataset.backgroundColor = epsColors.economic;
        } else if (dataset.label?.includes('Objective')) {
          newDataset.backgroundColor = epsColors.objective;
        }
      }
      // For line charts (power score timeline)
      else if (chartConfig.type === 'line') {
        // Alternate between team colors based on index
        const colorPalette = index < 5 ? teamPalettes.team100 : teamPalettes.team200;
        const colorIndex = index % 5;
        newDataset.borderColor = colorPalette[colorIndex];
        newDataset.backgroundColor = colorPalette[colorIndex];
        newDataset.borderWidth = 2.5; // Slightly thicker lines
        newDataset.tension = 0.3; // Smooth curves
      }
      // For gold efficiency (regular bar chart)
      else if (chartConfig.type === 'bar' && !isHorizontal) {
        // Keep team-based colors but ensure they're visible
        if (Array.isArray(dataset.backgroundColor)) {
          newDataset.backgroundColor = dataset.backgroundColor.map((color: string) => {
            // If it's a blue-ish color (team 100), use accent
            if (color.includes('3498db') || color.toLowerCase().includes('blue')) {
              return themeColors.accent;
            }
            // If it's a red-ish color (team 200), use primary
            return themeColors.primary;
          });
        }
      }
      
      return newDataset;
    });
  }
  
  // Build clean configuration with theme integration
  const config: ChartConfiguration = {
    type: chartConfig.type as any,
    data: themedData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: chartConfig.options?.indexAxis || 'x',
      layout: {
        padding: {
          top: 20, // Add space between legend and graph
        },
      },
      // Better interaction for stacked charts
      interaction: {
        mode: isHorizontal ? 'y' as const : 'index' as const,
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top' as const,
          align: 'center' as const,
          onClick: enableLegendClick ? undefined : () => {}, // Use default click behavior if enabled, otherwise disable
          labels: {
            color: getThemeColor('--region-text'),
            font: {
              size: 13,
              family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            },
            padding: 15,
            usePointStyle: true,
            pointStyle: 'circle',
          },
        },
        title: {
          display: !!title,
          text: title || '',
          color: getThemeColor('--region-text'),
          font: {
            size: 18,
            weight: 'bold' as const,
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          },
          padding: {
            top: 0,
            bottom: 15,
          },
        },
        tooltip: {
          enabled: true,
          backgroundColor: getThemeColor('--region-secondary') + 'F5', // Add opacity
          titleColor: getThemeColor('--region-primary'),
          bodyColor: getThemeColor('--region-text'),
          borderColor: getThemeColor('--region-panel-border'),
          borderWidth: 1,
          titleFont: {
            size: 14,
            weight: 'bold' as const,
          },
          bodyFont: {
            size: 13,
          },
          padding: 12,
          cornerRadius: 8,
          displayColors: true,
          boxPadding: 6,
          // Sort tooltip items by value (highest to lowest)
          itemSort: (a: any, b: any) => {
            return b.parsed.y - a.parsed.y;
          },
          callbacks: {
            // Format title to show "X minutes" for line charts
            title: (context: any) => {
              if (chartConfig.type === 'line' && context[0]) {
                const label = context[0].label;
                return `${label} ${label === '1' ? 'minute' : 'minutes'}`;
              }
              return context[0]?.label || '';
            },
          },
        },
      },
      scales: isHorizontal ? {
        // Horizontal bar chart (EPS Breakdown)
        x: {
          stacked: true,
          grid: {
            display: true,
            color: getThemeColor('--region-panel'),
            lineWidth: 1,
          },
          border: {
            display: true,
            color: getThemeColor('--region-panel-border'),
          },
          ticks: {
            color: getThemeColor('--region-text-secondary'),
            font: {
              size: 12,
            },
          },
          title: {
            display: true,
            text: 'Score',
            color: getThemeColor('--region-text'),
            font: {
              size: 13,
              weight: 'bold' as const,
            },
          },
        },
        y: {
          stacked: true,
          grid: {
            display: false, // Cleaner look for player names
          },
          border: {
            display: true,
            color: getThemeColor('--region-panel-border'),
          },
          ticks: {
            color: getThemeColor('--region-text'),
            font: {
              size: window.innerWidth < 768 ? 11 : 13, // Responsive font size
            },
            autoSkip: false, // Show all player names
          },
        },
      } : {
        // Vertical charts (line/bar)
        x: {
          grid: {
            display: true,
            color: getThemeColor('--region-panel'),
            lineWidth: 1,
          },
          border: {
            display: true,
            color: getThemeColor('--region-panel-border'),
          },
          ticks: {
            color: getThemeColor('--region-text-secondary'),
            font: {
              size: window.innerWidth < 768 ? 10 : 11,
            },
            maxRotation: 45,
            minRotation: 0,
          },
          title: {
            display: true,
            text: chartConfig.type === 'line' ? 'Time (Minutes)' : 'Players',
            color: getThemeColor('--region-text'),
            font: {
              size: 13,
              weight: 'bold' as const,
            },
          },
        },
        y: {
          grid: {
            display: true,
            color: getThemeColor('--region-panel'),
            lineWidth: 1,
          },
          border: {
            display: true,
            color: getThemeColor('--region-panel-border'),
          },
          ticks: {
            color: getThemeColor('--region-text-secondary'),
            font: {
              size: window.innerWidth < 768 ? 10 : 11,
            },
          },
          title: {
            display: true,
            text: 'Score',
            color: getThemeColor('--region-text'),
            font: {
              size: 13,
              weight: 'bold' as const,
            },
          },
        },
      },
    },
  };

  // Responsive height calculation
  const defaultHeight = isHorizontal 
    ? Math.max(450, (chartConfig.data?.labels?.length || 10) * (window.innerWidth < 768 ? 40 : 45))
    : (window.innerWidth < 768 ? 350 : 400); // Normal height for line charts
  
  const chartHeight = height || defaultHeight;

  return (
    <div className={styles.chartContainer} style={{ height: `${chartHeight}px` }}>
      <Chart key={chartKey} ref={chartRef} type={config.type} data={config.data} options={config.options} />
    </div>
  );
}

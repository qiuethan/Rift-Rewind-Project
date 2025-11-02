import { useState } from 'react';
import { useTheme } from '@/contexts';
import { getAllThemeIds, getThemeById } from '@/config';
import styles from './RegionSelector.module.css';

export default function RegionSelector() {
  const { theme, setTheme } = useTheme();
  const [isExpanded, setIsExpanded] = useState(false);
  const allThemeIds = getAllThemeIds();
  
  // Sort themes alphabetically by name
  const sortedThemeIds = [...allThemeIds].sort((a, b) => {
    const themeA = getThemeById(a);
    const themeB = getThemeById(b);
    return themeA.name.localeCompare(themeB.name);
  });

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTheme(e.target.value);
  };

  return (
    <div 
      className={styles.container}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
      title={`Current region: ${theme.name}`}
    >
      <div className={styles.icon}>🗺️</div>
      {isExpanded && (
        <select
          id="region-selector"
          value={theme.id}
          onChange={handleChange}
          className={styles.select}
        >
          {sortedThemeIds.map((id) => {
            const regionTheme = getThemeById(id);
            return (
              <option key={id} value={id}>
                {regionTheme.name}
              </option>
            );
          })}
        </select>
      )}
    </div>
  );
}

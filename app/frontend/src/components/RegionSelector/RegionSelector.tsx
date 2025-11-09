import { useTheme } from '@/contexts';
import { getAllThemeIds, getThemeById } from '@/config';
import styles from './RegionSelector.module.css';

export default function RegionSelector() {
  const { theme, setTheme } = useTheme();
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
      title={`Current region: ${theme.name}`}
    >
      <div className={styles.icon}>
        <img src="/img/regions/map_icon.webp" alt="Map" />
      </div>
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
    </div>
  );
}

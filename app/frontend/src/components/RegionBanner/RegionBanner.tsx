import { useTheme } from '@/contexts';
import styles from './RegionBanner.module.css';

interface RegionBannerProps {
  className?: string;
}

export default function RegionBanner({ className = '' }: RegionBannerProps) {
  const { theme } = useTheme();

  return (
    <div className={`${styles.banner} ${className}`}>
      <div className={styles.content}>
        <span className={styles.label}>Analyzing from the perspective of</span>
        <span className={styles.regionName}>{theme.name}</span>
        <span className={styles.separator}>—</span>
        <span className={styles.tagline}>{theme.tagline}</span>
      </div>
      {theme.images.decorative && (
        <img
          src={theme.images.decorative}
          alt=""
          className={styles.decorative}
          aria-hidden="true"
        />
      )}
    </div>
  );
}

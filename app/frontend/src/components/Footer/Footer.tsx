import styles from './Footer.module.css';
import RegionSelector from '../RegionSelector';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.left}>
          <span className={styles.copyright}>
            © 2025 Rift Rewind. All rights reserved.
          </span>
        </div>
        
        <div className={styles.center}>
          <RegionSelector />
        </div>
        
        <div className={styles.right}>
          <span className={styles.disclaimer}>
            Rift Rewind isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties.
          </span>
        </div>
      </div>
    </footer>
  );
}

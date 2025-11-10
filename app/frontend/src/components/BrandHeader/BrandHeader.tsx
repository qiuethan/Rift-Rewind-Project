import styles from './BrandHeader.module.css';

interface BrandHeaderProps {
  size?: 'large' | 'small';
}

export default function BrandHeader({ size = 'large' }: BrandHeaderProps) {
  return (
    <header className={`${styles.header} ${styles[size]}`}>
      <h1 className={styles.title}>
        Heimer Academy
        <img
          src="https://heimerdinger.lol/img/heimerdinger-emote.webp"
          alt="Heimerdinger emote"
          className={styles.emoji}
        />
      </h1>
      <p className={styles.subtitle}>learning league the <span className={styles.rightWord}>RIGHT</span> way</p>
    </header>
  );
}
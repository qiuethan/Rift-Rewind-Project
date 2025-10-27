import { Card } from '@/components';
import styles from './AccountInfo.module.css';

interface AccountInfoProps {
  user: {
    email: string;
    user_id: string;
  };
}

export default function AccountInfo({ user }: AccountInfoProps) {
  return (
    <Card title="Account Info">
      <div className={styles.info}>
        <div className={styles.infoRow}>
          <span className={styles.label}>Email:</span>
          <span className={styles.value}>{user.email}</span>
        </div>
        <div className={styles.infoRow}>
          <span className={styles.label}>User ID:</span>
          <span className={styles.value}>{user.user_id}</span>
        </div>
      </div>
    </Card>
  );
}

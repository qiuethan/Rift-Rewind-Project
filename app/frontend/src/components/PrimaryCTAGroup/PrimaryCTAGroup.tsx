import { useNavigate } from 'react-router-dom';
import styles from './PrimaryCTAGroup.module.css';
import { Button } from '@/components';
import { ROUTES } from '@/config';

export default function PrimaryCTAGroup() {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <Button
        variant="secondary"
        onClick={() => navigate(ROUTES.DASHBOARD)}
        className={styles.ctaButton}
      >
        Monitor Your Progress
      </Button>
      <Button
        onClick={() => navigate(ROUTES.RECOMMEND)}
        className={styles.ctaButton}
      >
        Learn a New Champion!
      </Button>
    </div>
  );
}
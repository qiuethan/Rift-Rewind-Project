import { useNavigate } from 'react-router-dom';
import { Button, Card } from '@/components';
import { ROUTES } from '@/config';
import styles from './QuickActions.module.css';

interface QuickActionsProps {
  summoner: any;
  onLinkAccount: () => void;
}

export default function QuickActions({ summoner, onLinkAccount }: QuickActionsProps) {
  const navigate = useNavigate();

  return (
    <Card title="Quick Actions">
      <div className={styles.actions}>
        <Button fullWidth onClick={() => navigate(ROUTES.ANALYTICS)}>
          View Analytics
        </Button>
        <Button fullWidth onClick={() => navigate(ROUTES.CHAMPIONS)}>
          Champion Recommendations
        </Button>
        <Button fullWidth onClick={onLinkAccount}>
          {summoner ? 'Update' : 'Link'} League Account
        </Button>
      </div>
    </Card>
  );
}

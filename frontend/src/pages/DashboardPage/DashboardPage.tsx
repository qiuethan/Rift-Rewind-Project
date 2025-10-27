import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './DashboardPage.module.css';
import { Button, Card } from '@/components';
import { authActions } from '@/actions/auth';
import { playersActions } from '@/actions/players';
import { ROUTES } from '@/config';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [summoner, setSummoner] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    // Check if authenticated
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }

    // Get user data
    const userData = authActions.getCurrentUser();
    setUser(userData);

    // Try to get summoner data
    const summonerResult = await playersActions.getSummoner();
    if (summonerResult.success) {
      setSummoner(summonerResult.data);
    }

    setLoading(false);
  };

  const handleLogout = async () => {
    await authActions.logout();
    navigate(ROUTES.LOGIN);
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Dashboard</h1>
        <Button variant="secondary" onClick={handleLogout}>
          Logout
        </Button>
      </div>

      <div className={styles.grid}>
        <Card title="Account Info">
          <div className={styles.info}>
            <div className={styles.infoRow}>
              <span className={styles.label}>Email:</span>
              <span className={styles.value}>{user?.email}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.label}>User ID:</span>
              <span className={styles.value}>{user?.user_id}</span>
            </div>
          </div>
        </Card>

        <Card title="Summoner Info">
          {summoner ? (
            <div className={styles.info}>
              <div className={styles.infoRow}>
                <span className={styles.label}>Summoner:</span>
                <span className={styles.value}>{summoner.summoner_name}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.label}>Region:</span>
                <span className={styles.value}>{summoner.region}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.label}>Level:</span>
                <span className={styles.value}>{summoner.summoner_level}</span>
              </div>
            </div>
          ) : (
            <div className={styles.empty}>
              <p>No summoner linked yet</p>
              <Button onClick={() => navigate(ROUTES.PROFILE)}>Link Account</Button>
            </div>
          )}
        </Card>

        <Card title="Quick Actions">
          <div className={styles.actions}>
            <Button fullWidth onClick={() => navigate(ROUTES.ANALYTICS)}>
              View Analytics
            </Button>
            <Button fullWidth onClick={() => navigate(ROUTES.CHAMPIONS)}>
              Champion Recommendations
            </Button>
            <Button fullWidth onClick={() => navigate(ROUTES.PROFILE)}>
              Profile Settings
            </Button>
          </div>
        </Card>

        <Card title="Welcome to Rift Rewind! 🎮">
          <div className={styles.welcome}>
            <p>
              Rift Rewind is your AI-powered League of Legends analytics platform. Get personalized
              insights, champion recommendations, and performance analysis.
            </p>
            <ul className={styles.features}>
              <li>📊 Match performance analysis</li>
              <li>🏆 Champion recommendations based on your playstyle</li>
              <li>📈 Skill progression tracking</li>
              <li>🤖 AI-powered insights and tips</li>
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
}

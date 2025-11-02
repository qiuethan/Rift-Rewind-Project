import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import styles from './ChampionDetailPage.module.css';
import { Button, Card, Navbar } from '@/components';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';
import { useSummoner, useTheme } from '@/contexts';
import { getChampionIconUrl, getChampionKey } from '@/constants';

// Temporary dummy data with regions for theme switching
const CHAMPION_REGIONS: { [key: string]: string } = {
  'ahri': 'ionia',
  'yasuo': 'ionia',
  'zed': 'ionia',
  'lux': 'demacia',
  'jinx': 'piltover',
  'thresh': 'shadowisles',
  'leesin': 'ionia',
  'ezreal': 'piltover',
  'vayne': 'demacia',
  'katarina': 'noxus',
  'darius': 'noxus',
  'garen': 'demacia',
};

export default function ChampionDetailPage() {
  const navigate = useNavigate();
  const { championName } = useParams<{ championName: string }>();
  const { summoner } = useSummoner();
  const { setTheme } = useTheme();
  const [user, setUser] = useState<any>(null);

  // Find champion from summoner's mastery data
  const champion = summoner?.champion_masteries?.find((c: any) => {
    const championId = c.championId || c.champion_id;
    const name = getChampionKey(championId);
    return name.toLowerCase() === championName?.toLowerCase();
  });

  const championId = champion ? (champion.championId || champion.champion_id) : 0;
  const championKey = getChampionKey(championId);
  const masteryLevel = champion ? (champion.championLevel || champion.champion_level || 0) : 0;
  const masteryPoints = champion ? (champion.championPoints || champion.champion_points || 0) : 0;

  useEffect(() => {
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }
    const userData = authActions.getCurrentUser();
    setUser(userData);
  }, [navigate]);

  // Set theme based on champion's region
  useEffect(() => {
    const region = CHAMPION_REGIONS[championName?.toLowerCase() || ''] || 'piltover';
    setTheme(region);
  }, [championName, setTheme]);

  if (!champion && !summoner) {
    return (
      <>
        <Navbar user={user} summoner={summoner} />
        <div className={styles.container}>
          <Card>
            <div className={styles.notFound}>
              <h2>Champion Not Found</h2>
              <Button onClick={() => navigate(ROUTES.CHAMPIONS)}>
                Back to Champions
              </Button>
            </div>
          </Card>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar user={user} summoner={summoner} />
      <div className={styles.container}>
        <div className={styles.backButton}>
          <Button variant="secondary" onClick={() => navigate(ROUTES.CHAMPIONS)}>
            ← Back to Champions
          </Button>
        </div>

        <div className={styles.championHeader}>
          <div className={styles.championIcon}>
            <img
              src={getChampionIconUrl(championKey)}
              alt={championKey}
              className={styles.championImage}
            />
            <div className={styles.masteryBadge}>
              Level {masteryLevel}
            </div>
          </div>
          <div className={styles.championInfo}>
            <h1 className={styles.championName}>{championKey}</h1>
            <p className={styles.championSubtitle}>
              {masteryPoints.toLocaleString()} Mastery Points
            </p>
          </div>
        </div>

        <div className={styles.statsGrid}>
          <Card title="Mastery Info">
            <div className={styles.statsContent}>
              <div className={styles.statItem}>
                <span className={styles.statLabel}>Mastery Level</span>
                <span className={styles.statValue}>{masteryLevel}</span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.statLabel}>Mastery Points</span>
                <span className={styles.statValue}>{masteryPoints.toLocaleString()}</span>
              </div>
            </div>
          </Card>

          <Card title="Mastery Progress">
            <div className={styles.masteryContent}>
              <div className={styles.masteryLevel}>
                <span className={styles.masteryLabel}>Current Level</span>
                <span className={styles.masteryValue}>{masteryLevel}</span>
              </div>
              <div className={styles.masteryPoints}>
                <span className={styles.masteryLabel}>Total Points</span>
                <span className={styles.masteryValue}>
                  {masteryPoints.toLocaleString()}
                </span>
              </div>
              <div className={styles.masteryBar}>
                <div 
                  className={styles.masteryProgress}
                  style={{ width: `${Math.min((masteryLevel / 7) * 100, 100)}%` }}
                />
              </div>
              <p className={styles.masteryNote}>
                {masteryLevel >= 7 
                  ? '🏆 Maximum mastery achieved!' 
                  : `${7 - masteryLevel} level${7 - masteryLevel > 1 ? 's' : ''} until max mastery`}
              </p>
            </div>
          </Card>
        </div>

        <Card title="Recent Match History">
          <div className={styles.matchHistory}>
            <p className={styles.comingSoon}>
              Match history for this champion coming soon...
            </p>
          </div>
        </Card>
      </div>
    </>
  );
}

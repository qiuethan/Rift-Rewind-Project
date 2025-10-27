import { Card } from '@/components';
import { getChampionKey, getChampionIconUrl, FALLBACK_ICON_URL } from '@/constants';
import styles from './TopChampions.module.css';

interface TopChampionsProps {
  topChampions: any[];
  totalMasteryScore?: number;
}

export default function TopChampions({ topChampions, totalMasteryScore }: TopChampionsProps) {
  if (!topChampions || topChampions.length === 0) {
    return null;
  }

  return (
    <Card title="Top Champions">
      <div className={styles.championsGrid}>
        {topChampions.slice(0, 4).map((champ: any) => {
          // Handle both camelCase (from API) and snake_case (from DB)
          const championId = champ.championId || champ.champion_id;
          const championLevel = champ.championLevel || champ.champion_level;
          const championPoints = champ.championPoints || champ.champion_points;
          const championKey = getChampionKey(championId);

          return (
            <div key={championId} className={styles.championCard}>
              <img
                src={getChampionIconUrl(championKey)}
                alt={championKey}
                className={styles.championIcon}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = FALLBACK_ICON_URL;
                }}
              />
              <div className={styles.championInfo}>
                <div className={styles.championName}>{championKey}</div>
                <div className={styles.championLevel}>Level {championLevel}</div>
                <div className={styles.championPoints}>
                  {(championPoints / 1000).toFixed(0)}k points
                </div>
              </div>
            </div>
          );
        })}
      </div>
      {totalMasteryScore && (
        <div className={styles.masteryScore}>
          Total Mastery Score: <strong>{totalMasteryScore.toLocaleString()}</strong>
        </div>
      )}
    </Card>
  );
}

import { Card, Spinner } from '@/components';
import { getChampionKey, getChampionIconUrl } from '@/constants';
import styles from './RecentGames.module.css';

interface RecentGame {
  match_id: string;
  game_mode: string;
  game_duration: number;
  game_creation: number;
  champion_id: number;
  champion_name: string;
  kills: number;
  deaths: number;
  assists: number;
  win: boolean;
  cs: number;
  gold: number;
  damage: number;
  vision_score: number;
  items: number[];
}

interface RecentGamesProps {
  recentGames?: RecentGame[];
  loading?: boolean;
}

export default function RecentGames({ recentGames, loading }: RecentGamesProps) {
  if (loading) {
    return (
      <Card title="Recent Games">
        <div className={styles.loading}>
          <Spinner />
          <p>Loading recent games...</p>
        </div>
      </Card>
    );
  }

  if (!recentGames || recentGames.length === 0) {
    return (
      <Card title="Recent Games">
        <div className={styles.empty}>
          <p>No recent games found</p>
        </div>
      </Card>
    );
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const formatGameTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    // Show relative time for recent games
    if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      // Show actual date for older games
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    }
  };

  const formatKDA = (kills: number, deaths: number, assists: number) => {
    return `${kills} / ${deaths} / ${assists}`;
  };

  const getKDAColor = (kills: number, deaths: number, assists: number) => {
    const kda = deaths === 0 ? kills + assists : (kills + assists) / deaths;
    if (kda >= 4) return styles.kdaExcellent;
    if (kda >= 3) return styles.kdaGood;
    if (kda >= 2) return styles.kdaAverage;
    return styles.kdaPoor;
  };

  const formatGameMode = (mode: string) => {
    const modes: { [key: string]: string } = {
      'CLASSIC': 'Ranked',
      'ARAM': 'ARAM',
      'CHERRY': 'Arena',
      'NEXUSBLITZ': 'Nexus Blitz',
      'TUTORIAL_MODULE_1': 'Tutorial',
      'TUTORIAL_MODULE_2': 'Tutorial',
      'TUTORIAL_MODULE_3': 'Tutorial',
    };
    return modes[mode] || mode;
  };

  const getItemIconUrl = (itemId: number) => {
    if (itemId === 0) return null;
    return `https://ddragon.leagueoflegends.com/cdn/15.21.1/img/item/${itemId}.png`;
  };

  return (
    <Card title="Recent Games">
      <div className={styles.gamesContainer}>
        {recentGames.map((game) => {
          const championKey = getChampionKey(game.champion_id);
          const kdaColor = getKDAColor(game.kills, game.deaths, game.assists);

          return (
            <div
              key={game.match_id}
              className={`${styles.gameCard} ${game.win ? styles.win : styles.loss}`}
            >
              <div className={styles.gameResult}>
                <span className={styles.resultText}>{game.win ? 'Victory' : 'Defeat'}</span>
                <span className={styles.gameMode}>{formatGameMode(game.game_mode)}</span>
                <span className={styles.duration}>{formatDuration(game.game_duration)}</span>
                <span className={styles.gameTime}>{formatGameTime(game.game_creation)}</span>
              </div>

              <div className={styles.gameDetails}>
                <div className={styles.championSection}>
                  <img
                    src={getChampionIconUrl(championKey)}
                    alt={game.champion_name}
                    className={styles.championIcon}
                  />
                  <span className={styles.championName}>{game.champion_name}</span>
                </div>

                <div className={styles.statsSection}>
                  <div className={styles.kda}>
                    <span className={kdaColor}>{formatKDA(game.kills, game.deaths, game.assists)}</span>
                  </div>
                  <div className={styles.stats}>
                    <span>{game.cs} CS</span>
                    <span>{(game.gold / 1000).toFixed(1)}k Gold</span>
                  </div>
                </div>

                <div className={styles.itemsSection}>
                  {game.items.map((itemId, index) => (
                    <div key={index} className={styles.itemSlot}>
                      {itemId !== 0 && (
                        <img
                          src={getItemIconUrl(itemId)!}
                          alt={`Item ${itemId}`}
                          className={styles.itemIcon}
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

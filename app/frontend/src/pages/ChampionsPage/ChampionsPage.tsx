import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ChampionsPage.module.css';
import { Navbar, Spinner } from '@/components';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';
import { useSummoner } from '@/contexts';
import { getChampionIconUrl, getChampionKey } from '@/constants';

interface ChampionMastery {
  championId?: number;
  champion_id?: number;
  championLevel?: number;
  champion_level?: number;
  championPoints?: number;
  champion_points?: number;
  championName?: string;
}

export default function ChampionsPage() {
  const navigate = useNavigate();
  const { summoner, loading: summonerLoading } = useSummoner();
  const [user, setUser] = useState<any>(null);
  const [champions, setChampions] = useState<ChampionMastery[]>([]);

  // Check authentication
  useEffect(() => {
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }
    const userData = authActions.getCurrentUser();
    setUser(userData);
  }, [navigate]);

  // Load champion masteries from summoner data
  useEffect(() => {
    if (summoner?.champion_masteries) {
      setChampions(summoner.champion_masteries);
    }
  }, [summoner]);

  const getMasteryColor = (level: number) => {
    if (level >= 7) return styles.mastery7;
    if (level >= 5) return styles.mastery5;
    return styles.mastery4;
  };

  const getChampionId = (champion: ChampionMastery) => {
    return champion.championId || champion.champion_id || 0;
  };

  const getChampionLevel = (champion: ChampionMastery) => {
    return champion.championLevel || champion.champion_level || 0;
  };

  const getChampionPoints = (champion: ChampionMastery) => {
    return champion.championPoints || champion.champion_points || 0;
  };

  if (summonerLoading) {
    return (
      <>
        <Navbar user={user} summoner={summoner} />
        <div className={styles.container}>
          <div className={styles.loading}>
            <Spinner size="large" />
            <span>Loading champions...</span>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar user={user} summoner={summoner} />
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Champion Mastery</h1>
          <p className={styles.subtitle}>
            {champions.length} champions played • {summoner?.total_mastery_score?.toLocaleString() || 0} total mastery points
          </p>
        </div>

        {champions.length === 0 ? (
          <div className={styles.noChampions}>
            <p>No champion mastery data available. Play some games to see your champions!</p>
          </div>
        ) : (
          <div className={styles.championsGrid}>
            {champions.map((champion, index) => {
              const championId = getChampionId(champion);
              const championName = getChampionKey(championId);
              const masteryLevel = getChampionLevel(champion);
              const masteryPoints = getChampionPoints(champion);

              return (
                <div
                  key={championId || index}
                  className={styles.championCard}
                  onClick={() => navigate(`/champion/${championName.toLowerCase()}`)}
                >
                  <div className={styles.championImageWrapper}>
                    <img
                      src={getChampionIconUrl(championName)}
                      alt={championName}
                      className={styles.championIcon}
                    />
                    <div className={`${styles.masteryBadge} ${getMasteryColor(masteryLevel)}`}>
                      {masteryLevel}
                    </div>
                  </div>
                  <div className={styles.championInfo}>
                    <h3 className={styles.championName}>{championName}</h3>
                    <p className={styles.championPoints}>
                      {(masteryPoints / 1000).toFixed(0)}k points
                    </p>
                    <div className={styles.championMeta}>
                      <span>Level {masteryLevel}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}

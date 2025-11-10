import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TrackedChampions.module.css';
import { Card, Spinner } from '@/components';
import { getTrackedChampions, trackChampion, untrackChampion } from '@/api/trackedChampions';
import type { TrackedChampion } from '@/api/trackedChampions';
import { getChampionIconUrl, getChampionKey } from '@/constants';
import { ROUTES } from '@/config';

interface ChampionMastery {
  championId?: number;
  champion_id?: number;
  championName?: string;
}

interface TrackedChampionsProps {
  championMasteries?: ChampionMastery[];
  onTrackingChange?: () => void;
}

export default function TrackedChampions({ championMasteries, onTrackingChange }: TrackedChampionsProps) {
  const navigate = useNavigate();
  const [trackedChampions, setTrackedChampions] = useState<TrackedChampion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [maxAllowed, setMaxAllowed] = useState(3);

  // Fetch tracked champions
  useEffect(() => {
    fetchTrackedChampions();
  }, []);

  const fetchTrackedChampions = async () => {
    try {
      setLoading(true);
      const response = await getTrackedChampions();
      setTrackedChampions(response.tracked_champions);
      setMaxAllowed(response.max_allowed);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch tracked champions:', err);
      setError('Failed to load tracked champions');
    } finally {
      setLoading(false);
    }
  };

  const handleUntrack = async (championId: number) => {
    try {
      await untrackChampion(championId);
      await fetchTrackedChampions();
      // Notify parent to update recommendation buttons
      onTrackingChange?.();
    } catch (err) {
      console.error('Failed to untrack champion:', err);
      alert('Failed to untrack champion. Please try again.');
    }
  };

  const hasPlayedChampion = (championId: number): boolean => {
    if (!championMasteries || championMasteries.length === 0) {
      return false;
    }
    return championMasteries.some(mastery => {
      const masteryId = mastery.championId || mastery.champion_id;
      return masteryId === championId;
    });
  };

  const handleChampionClick = (championId: number) => {
    if (hasPlayedChampion(championId)) {
      const championName = getChampionKey(championId);
      navigate(`/champion/${championName.toLowerCase()}`, { state: { from: 'recommend' } });
    }
  };

  if (loading) {
    return (
      <Card className={styles.trackedCard}>
        <div className={styles.loading}>
          <Spinner size="medium" />
        </div>
      </Card>
    );
  }

  return (
    <Card className={styles.trackedCard}>
      <div className={styles.header}>
        <h2 className={styles.title}>Tracked Champions</h2>
        <span className={styles.count}>
          {trackedChampions.length} / {maxAllowed}
        </span>
      </div>

      {error && (
        <div className={styles.error}>
          <p>{error}</p>
        </div>
      )}

      {trackedChampions.length === 0 ? (
        <div className={styles.empty}>
          <p>No champions tracked yet</p>
          <p className={styles.hint}>Track champions from the recommendations below to monitor your progress!</p>
        </div>
      ) : (
        <div className={styles.championGrid}>
          {trackedChampions.map((tracked) => {
            const championName = getChampionKey(tracked.champion_id);
            const hasPlayed = hasPlayedChampion(tracked.champion_id);
            const isClickable = hasPlayed;
            
            // Get mastery info if champion has been played
            const championMastery = championMasteries?.find(m => {
              const masteryId = m.championId || m.champion_id;
              return masteryId === tracked.champion_id;
            });
            
            const masteryLevel = championMastery ? (championMastery.championLevel || (championMastery as any).champion_level || 0) : 0;
            const masteryPoints = championMastery ? (championMastery.championPoints || (championMastery as any).champion_points || 0) : 0;
            
            const getMasteryColor = (level: number) => {
              if (level >= 7) return styles.mastery7;
              if (level >= 5) return styles.mastery5;
              if (level >= 4) return styles.mastery4;
              return styles.mastery1;
            };

            return (
              <div
                key={tracked.champion_id}
                className={`${styles.championCard} ${!hasPlayed ? styles.greyedOut : ''}`}
                onClick={() => isClickable && handleChampionClick(tracked.champion_id)}
              >
                <button
                  className={styles.untrackButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleUntrack(tracked.champion_id);
                  }}
                  title="Remove from tracked"
                >
                  ✕
                </button>
                <div className={styles.championImageWrapper}>
                  <img
                    src={getChampionIconUrl(championName)}
                    alt={championName}
                    className={styles.championIcon}
                  />
                  {hasPlayed && masteryLevel > 0 && (
                    <div className={`${styles.masteryBadge} ${getMasteryColor(masteryLevel)}`}>
                      {masteryLevel}
                    </div>
                  )}
                </div>
                <div className={styles.championInfo}>
                  <h3 className={styles.championName}>{championName}</h3>
                  {hasPlayed ? (
                    <>
                      <p className={styles.championPoints}>
                        {(masteryPoints / 1000).toFixed(0)}k points
                      </p>
                      <div className={styles.championMeta}>
                        <span>Level {masteryLevel}</span>
                      </div>
                    </>
                  ) : (
                    <span className={styles.noGamesLabel}>No games yet</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styles from './MatchDetailPage.module.css';
import { Navbar, Spinner } from '@/components';
import { authActions } from '@/actions/auth';
import { playersActions } from '@/actions/players';
import { useSummoner } from '@/contexts';
import { ROUTES } from '@/config';
import type { FullGameData } from '@/api/players';

export default function MatchDetailPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const navigate = useNavigate();
  const { summoner } = useSummoner();
  const [user, setUser] = useState<any>(null);
  const [match, setMatch] = useState<FullGameData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMatch();
  }, [matchId]);

  const loadMatch = async () => {
    // Check if authenticated
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }

    // Get user data
    const userData = authActions.getCurrentUser();
    setUser(userData);

    if (!matchId) {
      setError('No match ID provided');
      setLoading(false);
      return;
    }

    try {
      const result = await playersActions.getMatch(matchId);
      if (result.success && result.data) {
        setMatch(result.data);
      } else {
        setError(result.error || 'Failed to load match');
      }
    } catch (err) {
      setError('Failed to load match');
      console.error('Error loading match:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar user={user} summoner={summoner} />
      <div className={styles.container}>
        {loading ? (
          <div className={styles.loading}>
            <Spinner size="large" />
            <span>Loading match details...</span>
          </div>
        ) : error ? (
          <div className={styles.error}>
            <h2>Error</h2>
            <p>{error}</p>
            <button onClick={() => navigate(ROUTES.GAMES)}>Back to Games</button>
          </div>
        ) : match ? (
          <div className={styles.matchContent}>
            <div className={styles.header}>
              <button onClick={() => navigate(-1)} className={styles.backButton}>
                ← Back
              </button>
              <h1 className={styles.title}>Match Details</h1>
              <p className={styles.matchId}>{matchId}</p>
            </div>

            <div className={styles.matchInfo}>
              <h2>Match Information</h2>
              <pre className={styles.jsonData}>
                {JSON.stringify(match.match_data, null, 2)}
              </pre>
            </div>

            {match.timeline_data ? (
              <div className={styles.timelineInfo}>
                <h2>Timeline Data</h2>
                <pre className={styles.jsonData}>
                  {JSON.stringify(match.timeline_data, null, 2)}
                </pre>
              </div>
            ) : (
              <div className={styles.timelineInfo}>
                <h2>Timeline Data</h2>
                <p className={styles.noData}>Timeline data not available for this match.</p>
              </div>
            )}
          </div>
        ) : (
          <div className={styles.notFound}>
            <h2>Match not found</h2>
            <button onClick={() => navigate(ROUTES.GAMES)}>Back to Games</button>
          </div>
        )}
      </div>
    </>
  );
}

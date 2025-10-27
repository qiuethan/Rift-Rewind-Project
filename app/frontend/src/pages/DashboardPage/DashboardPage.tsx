import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './DashboardPage.module.css';
import { Button, Modal, Input, Navbar, Spinner } from '@/components';
import { authActions } from '@/actions/auth';
import { playersActions } from '@/actions/players';
import { ROUTES } from '@/config';
import { REGION_NAMES } from '@/constants';
import {
  SummonerInfo,
  TopChampions,
  RecentGames,
} from './components';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [summoner, setSummoner] = useState<any>(null);
  const [recentGames, setRecentGames] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [gamesLoading, setGamesLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Form fields
  const [gameName, setGameName] = useState('');
  const [tagLine, setTagLine] = useState('');
  const [region, setRegion] = useState('americas');


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

    try {
      // Try to get summoner data
      const summonerResult = await playersActions.getSummoner();
      if (summonerResult.success && summonerResult.data) {
        setSummoner(summonerResult.data);
        
        // Fetch recent games separately
        fetchRecentGames();
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentGames = async () => {
    setGamesLoading(true);
    try {
      const gamesResult = await playersActions.getRecentGames(10);
      if (gamesResult.success && gamesResult.data) {
        setRecentGames(gamesResult.data);
      }
    } catch (error) {
      console.error('Error loading recent games:', error);
    } finally {
      setGamesLoading(false);
    }
  };

  const handleOpenModal = () => {
    // Pre-fill form if summoner exists
    if (summoner?.game_name) {
      setGameName(summoner.game_name);
    }
    if (summoner?.tag_line) {
      setTagLine(summoner.tag_line);
    }
    if (summoner?.region) {
      setRegion(summoner.region);
    }
    setIsModalOpen(true);
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    const result = await playersActions.linkAccount({
      game_name: gameName,
      tag_line: tagLine,
      region,
    });

    if (result.success) {
      setSuccess('League of Legends account linked successfully!');
      setSummoner(result.data);
      
      // Refetch recent games after updating account
      fetchRecentGames();
      
      setTimeout(() => {
        setIsModalOpen(false);
        setSuccess(null);
      }, 1500);
    } else {
      setError(result.error || 'Failed to link account');
    }

    setSaving(false);
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <Spinner size="large" />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navbar user={user} summoner={summoner} />
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Dashboard</h1>
        </div>

      <div className={styles.grid}>
        <SummonerInfo summoner={summoner} onLinkAccount={handleOpenModal} />
        <div className={styles.topChampionsWide}>
          <TopChampions
            topChampions={summoner?.top_champions}
            totalMasteryScore={summoner?.total_mastery_score}
            loading={loading}
          />
        </div>
      </div>

      {summoner && (
        <div className={styles.recentGamesSection}>
          <RecentGames recentGames={recentGames} loading={gamesLoading} />
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Link League Account">
        <form onSubmit={handleSubmit} className={styles.modalForm}>
          <p className={styles.modalDescription}>
            Enter your Riot ID to link your League of Legends account. We'll fetch your
            summoner data including PUUID, summoner level, and profile icon.
          </p>

          <div className={styles.riotIdContainer}>
            <div className={styles.riotIdField}>
              <Input
                label="Game Name"
                type="text"
                value={gameName}
                onChange={(e) => setGameName(e.target.value)}
                placeholder="Hide on bush"
                required
                fullWidth
              />
            </div>
            <div className={styles.riotIdSeparator}>#</div>
            <div className={styles.riotIdField}>
              <Input
                label="Tag Line"
                type="text"
                value={tagLine}
                onChange={(e) => setTagLine(e.target.value)}
                placeholder="NA1"
                required
                fullWidth
              />
            </div>
          </div>

          <div className={styles.selectContainer}>
            <label className={styles.selectLabel}>Region</label>
            <select
              className={styles.select}
              value={region}
              onChange={(e) => setRegion(e.target.value)}
            >
              {Object.entries(REGION_NAMES).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {error && <div className={styles.modalError}>{error}</div>}
          {success && <div className={styles.modalSuccess}>{success}</div>}

          <Button type="submit" loading={saving} disabled={saving} fullWidth>
            {saving ? 'Linking...' : (summoner ? 'Update Account' : 'Link Account')}
          </Button>
        </form>
      </Modal>
      </div>
    </>
  );
}

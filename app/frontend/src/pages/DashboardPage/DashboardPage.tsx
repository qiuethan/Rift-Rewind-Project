import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './DashboardPage.module.css';
import { Button, Modal, Input, Navbar, Spinner, RegionBanner, SyncStatusModal } from '@/components';
import { authActions } from '@/actions/auth';
import { playersActions } from '@/actions/players';
import { ROUTES } from '@/config';
import { REGION_NAMES } from '@/constants';
import { useSummoner } from '@/contexts';
import {
  TopChampions,
  RecentGames,
} from './components';

const RECENT_GAMES_CACHE_KEY = 'rift_rewind_recent_games_cache';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

interface CachedRecentGamesData {
  games: any[];
  timestamp: number;
  puuid: string;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { summoner, loading: summonerLoading, refreshSummoner } = useSummoner();
  const [user, setUser] = useState<any>(null);
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
  const [showSyncModal, setShowSyncModal] = useState(false);


  useEffect(() => {
    loadData();
  }, []);

  // Set loading to false once summoner context finishes loading
  useEffect(() => {
    if (!summonerLoading) {
      setLoading(false);
    }
  }, [summonerLoading]);

  // Fetch recent games when summoner becomes available
  useEffect(() => {
    if (summoner && !summonerLoading) {
      fetchRecentGames();
    }
  }, [summoner, summonerLoading]);

  const loadData = async () => {
    // Check if authenticated
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }

    // Get user data
    const userData = authActions.getCurrentUser();
    setUser(userData);
    
    // Don't set loading to false yet - wait for summoner context to finish loading
    // This will be handled by the isLoading computed value below
  };

  const loadRecentGamesFromCache = (puuid: string): any[] | null => {
    try {
      const cached = localStorage.getItem(RECENT_GAMES_CACHE_KEY);
      if (!cached) return null;

      const data: CachedRecentGamesData = JSON.parse(cached);
      const now = Date.now();

      // Check if cache is valid (same user and not expired)
      if (data.puuid === puuid && (now - data.timestamp) < CACHE_DURATION) {
        return data.games;
      }

      // Cache expired or different user
      localStorage.removeItem(RECENT_GAMES_CACHE_KEY);
      return null;
    } catch (error) {
      console.error('Error loading recent games from cache:', error);
      return null;
    }
  };

  const saveRecentGamesToCache = (games: any[], puuid: string) => {
    try {
      const cacheData: CachedRecentGamesData = {
        games,
        timestamp: Date.now(),
        puuid
      };
      localStorage.setItem(RECENT_GAMES_CACHE_KEY, JSON.stringify(cacheData));
    } catch (error) {
      console.error('Error saving recent games to cache:', error);
    }
  };

  const fetchRecentGames = async (backgroundUpdate = false) => {
    if (!summoner?.puuid) return;

    // Try to load from cache first
    if (!backgroundUpdate) {
      const cachedGames = loadRecentGamesFromCache(summoner.puuid);
      if (cachedGames) {
        console.log('Loading recent games from cache:', cachedGames.length);
        setRecentGames(cachedGames);
        // Still fetch fresh data in background
        fetchRecentGames(true);
        return;
      }
    }

    if (!backgroundUpdate) {
      setGamesLoading(true);
    }

    try {
      const gamesResult = await playersActions.getRecentGames(10);
      if (gamesResult.success && gamesResult.data) {
        setRecentGames(gamesResult.data);
        // Save to cache
        saveRecentGamesToCache(gamesResult.data, summoner.puuid);
      }
    } catch (error) {
      console.error('Error loading recent games:', error);
    } finally {
      if (!backgroundUpdate) {
        setGamesLoading(false);
      }
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
      setIsModalOpen(false);
      
      // Show sync modal for 5 minutes
      setShowSyncModal(true);
      setTimeout(() => {
        setShowSyncModal(false);
      }, 5 * 60 * 1000); // 5 minutes
      
      // Refresh summoner in context
      await refreshSummoner();
      
      // Clear cache and refetch recent games after updating account
      localStorage.removeItem(RECENT_GAMES_CACHE_KEY);
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

  const isLoading = loading || summonerLoading;

  return (
    <>
      <Navbar user={user} summoner={summoner} onChangeSummonerAccount={handleOpenModal} />
      {isLoading ? (
        <div className={styles.container}>
          <div className={styles.loading}>
            <Spinner size="large" />
            <span>Loading...</span>
          </div>
        </div>
      ) : (
        <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.headerTop}>
            <button 
              className={styles.backButton}
              onClick={() => navigate(ROUTES.HOME)}
              aria-label="Back to main menu"
            >
              ← Back to Main Menu
            </button>
          </div>
          <h1 className={styles.title}>Dashboard</h1>
        </div>

      <div className={styles.grid}>
        <TopChampions
          champions={summoner?.champion_masteries}
          loading={loading}
        />
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
      
      <SyncStatusModal 
        isVisible={showSyncModal} 
        onDismiss={() => setShowSyncModal(false)} 
      />
        </div>
      )}
    </>
  );
}

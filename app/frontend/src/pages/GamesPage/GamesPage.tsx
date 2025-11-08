import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './GamesPage.module.css';
import { Button, Navbar, Spinner } from '@/components';
import { authActions } from '@/actions/auth';
import { playersActions } from '@/actions/players';
import { ROUTES } from '@/config';
import { useSummoner } from '@/contexts';
import { RecentGames } from '@/pages/DashboardPage/components';
import type { FullGameData } from '@/api/players';

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

// Helper function to convert FullGameData to RecentGame format
const convertToRecentGames = (fullGames: FullGameData[], summonerPuuid: string): RecentGame[] => {
  const converted = fullGames.map((game) => {
    const participants = game.match_data?.info?.participants || [];
    const playerData = participants.find((p: any) => p.puuid === summonerPuuid);
    
    if (!playerData) {
      return null;
    }
    
    const gameInfo = game.match_data?.info || {};
    
    return {
      match_id: game.match_id,
      game_mode: gameInfo.gameMode || 'CLASSIC',
      game_duration: gameInfo.gameDuration || 0,
      game_creation: gameInfo.gameCreation || 0,
      champion_id: playerData.championId,
      champion_name: playerData.championName,
      kills: playerData.kills,
      deaths: playerData.deaths,
      assists: playerData.assists,
      win: playerData.win,
      cs: (playerData.totalMinionsKilled || 0) + (playerData.neutralMinionsKilled || 0),
      gold: playerData.goldEarned,
      damage: playerData.totalDamageDealtToChampions,
      vision_score: playerData.visionScore,
      items: [
        playerData.item0,
        playerData.item1,
        playerData.item2,
        playerData.item3,
        playerData.item4,
        playerData.item5,
        playerData.item6,
      ],
    };
  }).filter((game): game is RecentGame => game !== null);
  
  return converted;
};

const CACHE_KEY = 'rift_rewind_games_cache';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

interface CachedGamesData {
  games: RecentGame[];
  timestamp: number;
  puuid: string;
  currentIndex: number;
}

export default function GamesPage() {
  const navigate = useNavigate();
  const { summoner, loading: summonerLoading } = useSummoner();
  const [user, setUser] = useState<any>(null);
  const [recentGames, setRecentGames] = useState<RecentGame[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const GAMES_PER_PAGE = 10;

  useEffect(() => {
    loadData();
  }, [summoner]);

  const loadData = async () => {
    // Check if authenticated
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }

    // Get user data
    const userData = authActions.getCurrentUser();
    setUser(userData);

    // Wait for summoner to load from context
    if (summonerLoading) {
      return;
    }

    if (summoner?.puuid) {
      // Try to load from cache first
      const cachedData = loadFromCache(summoner.puuid);
      if (cachedData) {
        setRecentGames(cachedData.games);
        setCurrentIndex(cachedData.currentIndex);
        setLoading(false);
        // Still fetch fresh data in background
        loadGames(0, summoner.puuid, true);
      } else {
        // Load initial games
        await loadGames(0, summoner.puuid);
      }
    } else {
      // No summoner linked, redirect to dashboard
      navigate(ROUTES.DASHBOARD);
    }
    
    setLoading(false);
  };

  const loadFromCache = (puuid: string): CachedGamesData | null => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (!cached) return null;

      const data: CachedGamesData = JSON.parse(cached);
      const now = Date.now();

      // Check if cache is valid (same user and not expired)
      if (data.puuid === puuid && (now - data.timestamp) < CACHE_DURATION) {
        return data;
      }

      // Cache expired or different user
      localStorage.removeItem(CACHE_KEY);
      return null;
    } catch (error) {
      console.error('Error loading from cache:', error);
      return null;
    }
  };

  const saveToCache = (games: RecentGame[], puuid: string, index: number) => {
    try {
      const cacheData: CachedGamesData = {
        games,
        timestamp: Date.now(),
        puuid,
        currentIndex: index
      };
      localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
    } catch (error) {
      console.error('Error saving to cache:', error);
    }
  };

  const loadGames = async (startIndex: number, summonerPuuid?: string, backgroundUpdate = false) => {
    if (!backgroundUpdate) {
      if (startIndex === 0) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
    }

    // Use provided puuid or fall back to state
    const puuid = summonerPuuid || summoner?.puuid;
    
    if (!puuid) {
      console.error('No summoner PUUID available');
      setLoading(false);
      setLoadingMore(false);
      return;
    }

    try {
      const result = await playersActions.getGames(startIndex, GAMES_PER_PAGE);
      
      if (result.success && result.data) {
        // If we got 0 games, there are no more to load
        if (result.data.length === 0) {
          setHasMore(false);
          return;
        }
        
        // Convert FullGameData to RecentGame format
        const convertedGames = convertToRecentGames(result.data, puuid);
        
        let updatedGames: RecentGame[];
        if (startIndex === 0) {
          updatedGames = convertedGames;
          setRecentGames(convertedGames);
        } else {
          setRecentGames(prev => {
            updatedGames = [...prev, ...convertedGames];
            return updatedGames;
          });
        }
        
        // Check if there are more games
        if (result.data.length < GAMES_PER_PAGE) {
          setHasMore(false);
        }
        
        const newIndex = startIndex + result.data.length;
        setCurrentIndex(newIndex);

        // Save to cache (only for initial load or when adding more)
        if (startIndex === 0) {
          saveToCache(convertedGames, puuid, newIndex);
        } else if (updatedGames!) {
          saveToCache(updatedGames, puuid, newIndex);
        }
      }
    } catch (error) {
      console.error('Error loading games:', error);
    } finally {
      if (!backgroundUpdate) {
        setLoading(false);
        setLoadingMore(false);
      }
    }
  };

  const handleLoadMore = () => {
    loadGames(currentIndex);
  };

  return (
    <>
      <Navbar user={user} summoner={summoner} />
      {loading ? (
        <div className={styles.container}>
          <div className={styles.loading}>
            <Spinner size="large" />
            <span>Loading games...</span>
          </div>
        </div>
      ) : (
        <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Match History</h1>
          <p className={styles.subtitle}>
            {recentGames.length} game{recentGames.length !== 1 ? 's' : ''} loaded
          </p>
        </div>

        <div className={styles.gamesContainer}>
          <RecentGames recentGames={recentGames} loading={false} showCard={false} />

          {recentGames.length > 0 && hasMore && (
            <div className={styles.loadMoreContainer}>
              <Button
                onClick={handleLoadMore}
                loading={loadingMore}
                disabled={loadingMore}
              >
                {loadingMore ? 'Loading...' : 'Load More Games'}
              </Button>
            </div>
          )}

          {!hasMore && recentGames.length > 0 && (
            <div className={styles.endMessage}>
              <p>You've reached the end of your match history</p>
            </div>
          )}

          {recentGames.length === 0 && (
            <div className={styles.emptyState}>
              <p>No games found. Link your account to see your match history.</p>
              <Button onClick={() => navigate(ROUTES.DASHBOARD)}>
                Go to Dashboard
              </Button>
            </div>
          )}
        </div>
        </div>
      )}
    </>
  );
}

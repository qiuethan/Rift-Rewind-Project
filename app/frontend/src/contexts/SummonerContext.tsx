import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { playersActions } from '@/actions/players';

interface SummonerData {
  id: string;
  summoner_name: string;
  game_name?: string;
  tag_line?: string;
  region: string;
  puuid: string;
  summoner_level: number;
  profile_icon_id: number;
  last_updated: string;
  top_champions?: any[];
  total_mastery_score?: number;
  total_mastery_level?: number;
}

interface SummonerContextType {
  summoner: SummonerData | null;
  loading: boolean;
  error: string | null;
  refreshSummoner: () => Promise<void>;
  setSummoner: (summoner: SummonerData | null) => void;
}

const SummonerContext = createContext<SummonerContextType | undefined>(undefined);

export function SummonerProvider({ children }: { children: ReactNode }) {
  const [summoner, setSummoner] = useState<SummonerData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSummoner = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await playersActions.getSummoner();
      if (result.success && result.data) {
        setSummoner(result.data);
      } else {
        // Check if it's an auth error (401)
        if (result.error?.includes('401') || result.error?.includes('Unauthorized')) {
          // Don't show error, user will be redirected to login by ProtectedRoute
          console.log('Auth error, session likely expired');
          setSummoner(null);
        } else {
          setError(result.error || 'Failed to load summoner');
          setSummoner(null);
        }
      }
    } catch (err) {
      setError('Failed to load summoner');
      setSummoner(null);
    } finally {
      setLoading(false);
    }
  };

  // Load summoner on mount
  useEffect(() => {
    refreshSummoner();
  }, []);

  return (
    <SummonerContext.Provider
      value={{
        summoner,
        loading,
        error,
        refreshSummoner,
        setSummoner,
      }}
    >
      {children}
    </SummonerContext.Provider>
  );
}

export function useSummoner() {
  const context = useContext(SummonerContext);
  if (context === undefined) {
    throw new Error('useSummoner must be used within a SummonerProvider');
  }
  return context;
}

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styles from './MatchDetailPage.module.css';
import { Navbar, Spinner, MatchAnalysisChart, GenerateAnalysisButton, HeimerdingerModal, SummonerLinkModal } from '@/components';
import { authActions } from '@/actions/auth';
import { playersActions } from '@/actions/players';
import { llmActions } from '@/actions/llm';
import { useSummoner } from '@/contexts';
import { ROUTES } from '@/config';
import type { FullGameData } from '@/api/players';
import { getCachedMatchAnalysis, cacheMatchAnalysis } from '@/utils/analysisCache';

export default function MatchDetailPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const navigate = useNavigate();
  const { summoner } = useSummoner();
  const [user, setUser] = useState<any>(null);
  const [match, setMatch] = useState<FullGameData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChampion, setSelectedChampion] = useState<string>('all');
  const [userChampion, setUserChampion] = useState<string>('');
  const [allChampions, setAllChampions] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'summary' | 'champion' | 'statistics'>('summary');
  const [championTabSelection, setChampionTabSelection] = useState<string>('');
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [analysisData, setAnalysisData] = useState<{ summary: string; fullAnalysis: string } | null>(null);
  const [cachedAnalysis, setCachedAnalysis] = useState<{ summary: string; fullAnalysis: string } | null>(null);
  const [showSummonerLinkModal, setShowSummonerLinkModal] = useState(false);

  useEffect(() => {
    loadMatch();
    // Load cached analysis if available
    if (matchId) {
      const cached = getCachedMatchAnalysis(matchId);
      if (cached) {
        const data = { summary: cached.summary, fullAnalysis: cached.fullAnalysis };
        setCachedAnalysis(data);
        setAnalysisData(data);
      }
    }
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
        
        // Extract all champion names from the chart data
        if (result.data.analysis?.charts?.powerScoreTimeline?.data?.datasets) {
          const championNames = result.data.analysis.charts.powerScoreTimeline.data.datasets
            .map((dataset: any) => {
              const label = dataset.label || '';
              // Extract champion name (before role if present, otherwise full name)
              const name = label.includes(' (') ? label.split(' (')[0] : label;
              return name.trim();
            })
            .filter((name: string) => name); // Remove empty names
          
          setAllChampions(championNames);
        }
        
        // Find user's champion in the match
        if (summoner?.puuid && result.data.match_data?.info?.participants) {
          const userParticipant = result.data.match_data.info.participants.find(
            (p: any) => p.puuid === summoner.puuid
          );
          if (userParticipant) {
            // Use the actual champion name for matching with analysis data
            const championName = userParticipant.championName;
            setUserChampion(championName);
            setChampionTabSelection(championName); // Default champion tab to user's champion
            console.log('User champion set to:', championName);
            // Don't set default - let user choose
          }
        }
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
  
  // Highlight selected champion while keeping others visible but dimmed
  const filterChartData = (chartConfig: any, chartType: 'line' | 'bar' | 'eps') => {
    if (!chartConfig || selectedChampion === 'all') return chartConfig;
    
    console.log(`[${chartType}] Original chart config:`, chartConfig);
    console.log(`[${chartType}] Original labels:`, chartConfig?.data?.labels);
    if (chartType === 'eps' && chartConfig?.data?.labels) {
      console.log(`[${chartType}] Label details:`, chartConfig.data.labels.map((l: any, i: number) => 
        `[${i}]: "${l}" (length: ${l?.length || 0}, type: ${typeof l})`
      ));
    }
    
    // Deep clone to avoid mutating original data
    const filtered = JSON.parse(JSON.stringify(chartConfig));
    
    console.log('After clone labels:', filtered?.data?.labels);
    
    // Helper to check if a label matches the selected champion
    const matchesChampion = (label: string) => {
      if (!label) return false;
      // Extract champion name (handle both with and without role parentheses)
      const labelName = label.includes(' (') ? label.split(' (')[0].trim() : label.trim();
      const selectedName = selectedChampion.includes(' (') ? selectedChampion.split(' (')[0].trim() : selectedChampion.trim();
      
      console.log(`Comparing: labelName="${labelName}" vs selectedName="${selectedName}"`);
      
      return labelName === selectedName;
    };
    
    if (chartType === 'eps') {
      // For EPS breakdown, highlight selected champion's bar
      if (filtered.data && filtered.data.labels && filtered.data.datasets) {
        // IMPORTANT: Keep all labels - they're the player names on Y-axis
        console.log('EPS Labels (raw):', filtered.data.labels);
        console.log('EPS Labels (expanded):', filtered.data.labels.map((l: any, i: number) => `[${i}]: "${l}"`));
        
        const championIndex = filtered.data.labels.findIndex((label: string) => matchesChampion(label));
        console.log('Selected champion index:', championIndex, 'for', selectedChampion);
        
        if (championIndex !== -1) {
          // Dim all bars except the selected one, but keep ALL labels
          filtered.data.datasets = filtered.data.datasets.map((dataset: any) => {
            const newData = dataset.data.map((value: any, idx: number) => {
              return idx === championIndex ? value : value * 0.3; // Dim others to 30%
            });
            
            return {
              ...dataset,
              data: newData,
            };
          });
        }
        
        // Ensure labels are preserved
        console.log('Final EPS labels:', filtered.data.labels);
      }
    } else if (chartType === 'bar') {
      // For gold efficiency bar chart, highlight selected champion
      if (filtered.data && filtered.data.labels && filtered.data.datasets) {
        const championIndex = filtered.data.labels.findIndex((label: string) => matchesChampion(label));
        
        if (championIndex !== -1) {
          filtered.data.datasets = filtered.data.datasets.map((dataset: any) => {
            // Adjust opacity for background colors
            const newBackgroundColors = Array.isArray(dataset.backgroundColor)
              ? dataset.backgroundColor.map((color: string, idx: number) => {
                  if (idx === championIndex) return color; // Full opacity for selected
                  // Add transparency to others
                  if (color && typeof color === 'string') {
                    if (color.startsWith('rgb(')) {
                      return color.replace('rgb(', 'rgba(').replace(')', ', 0.3)');
                    }
                    return color + '4D'; // Add alpha for hex colors
                  }
                  return color;
                })
              : dataset.backgroundColor;
            
            return {
              ...dataset,
              backgroundColor: newBackgroundColors
            };
          });
        }
      }
    } else {
      // For line charts (power score timeline), highlight selected line
      if (filtered.data && filtered.data.datasets) {
        console.log('Line chart filtering for:', selectedChampion);
        
        filtered.data.datasets = filtered.data.datasets.map((dataset: any) => {
          const label = dataset.label || '';
          const isSelected = matchesChampion(label);
          
          console.log(`Dataset label: "${label}", matches: ${isSelected}`);
          
          // Helper to add transparency to color
          const addTransparency = (color: string | undefined, opacity: number) => {
            if (!color || typeof color !== 'string') return color;
            if (color.startsWith('rgb(') && !color.startsWith('rgba(')) {
              return color.replace('rgb(', 'rgba(').replace(')', `, ${opacity})`);
            }
            if (color.startsWith('rgba(')) {
              // Already has alpha, replace it
              return color.replace(/[\d.]+\)$/g, `${opacity})`);
            }
            // Hex color - add alpha
            return color + Math.round(opacity * 255).toString(16).padStart(2, '0');
          };
          
          return {
            ...dataset,
            borderWidth: isSelected ? 4 : 1.5, // Thicker line for selected
            borderColor: isSelected 
              ? dataset.borderColor 
              : addTransparency(dataset.borderColor, 0.2), // Dim others more
            backgroundColor: isSelected
              ? dataset.backgroundColor
              : addTransparency(dataset.backgroundColor, 0.2),
          };
        });
      }
    }
    
    return filtered;
  };

  const handleGenerateAnalysis = async (): Promise<{ summary: string; fullAnalysis: string } | null> => {
    if (!matchId) return null;
    
    const result = await llmActions.analyzeMatch(matchId);
    
    if (result.success && result.data) {
      const data = {
        summary: result.data.summary,
        fullAnalysis: result.data.full_analysis,
      };
      setAnalysisData(data);
      setCachedAnalysis(data);
      // Cache in localStorage only on success
      cacheMatchAnalysis(matchId, data);
      return data;
    } else {
      // Return null - error will be shown in thought bubble
      return null;
    }
  };

  const handleOpenFullAnalysis = () => {
    setShowAnalysisModal(true);
  };

  return (
    <>
      <Navbar user={user} summoner={summoner} onChangeSummonerAccount={() => setShowSummonerLinkModal(true)} />
      <SummonerLinkModal
        isOpen={showSummonerLinkModal}
        onClose={() => setShowSummonerLinkModal(false)}
      />
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
              <div className={styles.headerTop}>
                <button onClick={() => navigate(-1)} className={styles.backButton}>
                  ← Back
                </button>
                <button onClick={() => setShowInfoModal(true)} className={styles.infoButton} title="Learn about metrics">
                  Metrics Info
                </button>
              </div>
              <div className={styles.headerCenter}>
                <h1 className={styles.title}>Match Analysis</h1>
                <p className={styles.matchId}>{matchId}</p>
              </div>
            </div>

            {/* Match Summary */}
            {match.match_data?.info && (
              <div className={styles.matchSummary}>
                <h2>Match Summary</h2>
                {(() => {
                  // Determine if user won
                  const userParticipant = summoner?.puuid 
                    ? match.match_data.info.participants?.find((p: any) => p.puuid === summoner.puuid)
                    : null;
                  const userWon = userParticipant?.win;
                  const hasUserData = !!userParticipant;
                  
                  return (
                    <>
                      {hasUserData && (
                        <div className={`${styles.winnerBanner} ${userWon ? styles.victoryBanner : styles.defeatBanner}`}>
                          <span className={styles.resultText}>
                            {userWon ? 'VICTORY' : 'DEFEAT'}
                          </span>
                        </div>
                      )}
                      <div className={styles.summaryGrid}>
                        <div className={styles.summaryItem}>
                          <span className={styles.summaryLabel}>Game Mode</span>
                          <span className={styles.summaryValue}>
                            {match.match_data.info.gameMode || 'Unknown'}
                          </span>
                        </div>
                        <div className={styles.summaryItem}>
                          <span className={styles.summaryLabel}>Duration</span>
                          <span className={styles.summaryValue}>
                            {Math.floor((match.match_data.info.gameDuration || 0) / 60)}m {(match.match_data.info.gameDuration || 0) % 60}s
                          </span>
                        </div>
                        <div className={styles.summaryItem}>
                          <span className={styles.summaryLabel}>Queue Type</span>
                          <span className={styles.summaryValue}>
                            {match.match_data.info.queueId === 420 ? 'Ranked Solo/Duo' :
                             match.match_data.info.queueId === 440 ? 'Ranked Flex' :
                             match.match_data.info.queueId === 450 ? 'ARAM' :
                             match.match_data.info.queueId === 400 ? 'Normal Draft' :
                             `Queue ${match.match_data.info.queueId}`}
                          </span>
                        </div>
                        <div className={styles.summaryItem}>
                          <span className={styles.summaryLabel}>Game Version</span>
                          <span className={styles.summaryValue}>
                            {match.match_data.info.gameVersion?.split('.').slice(0, 2).join('.') || 'Unknown'}
                          </span>
                        </div>
                        {match.match_data.info.participants && (
                          <>
                            <div className={styles.summaryItem}>
                              <span className={styles.summaryLabel}>Blue Team Kills</span>
                              <span className={styles.summaryValue}>
                                {match.match_data.info.participants
                                  .filter((p: any) => p.teamId === 100)
                                  .reduce((sum: number, p: any) => sum + (p.kills || 0), 0)}
                              </span>
                            </div>
                            <div className={styles.summaryItem}>
                              <span className={styles.summaryLabel}>Red Team Kills</span>
                              <span className={styles.summaryValue}>
                                {match.match_data.info.participants
                                  .filter((p: any) => p.teamId === 200)
                                  .reduce((sum: number, p: any) => sum + (p.kills || 0), 0)}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    </>
                  );
                })()}
              </div>
            )}

            {/* Tab Navigation */}
            <div className={styles.tabNavigation}>
              <button 
                className={`${styles.tab} ${activeTab === 'summary' ? styles.activeTab : ''}`}
                onClick={() => setActiveTab('summary')}
              >
                Summary
              </button>
              <button 
                className={`${styles.tab} ${activeTab === 'statistics' ? styles.activeTab : ''}`}
                onClick={() => setActiveTab('statistics')}
              >
                Statistics
              </button>
              <button 
                className={`${styles.tab} ${activeTab === 'champion' ? styles.activeTab : ''}`}
                onClick={() => setActiveTab('champion')}
              >
                Champion
              </button>
            </div>

            {match.analysis ? (
              <>
                {/* Summary Tab */}
                {activeTab === 'summary' && (
                  <div className={styles.tabContent}>
                    {/* User Performance Summary */}
                    {userChampion && match.analysis.rawStats?.epsScores && (
                      <div className={styles.performanceSummary}>
                        <div className={styles.performanceHeader}>
                          <img 
                            src={`https://ddragon.leagueoflegends.com/cdn/15.22.1/img/champion/${userChampion}.png`}
                            alt={userChampion}
                            className={styles.championIcon}
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                            }}
                          />
                          <h3>Your Performance as {userChampion}</h3>
                        </div>
                        {(() => {
                          const userEPS = match.analysis.rawStats.epsScores[userChampion];
                          
                          if (!userEPS) {
                            return <p className={styles.noData}>Performance data not available for {userChampion}</p>;
                          }
                          
                          // Find user's participant data
                          const userParticipant = match.match_data?.info?.participants?.find(
                            (p: any) => p.puuid === summoner?.puuid
                          );
                          
                          const allScores = Object.values(match.analysis.rawStats.epsScores) as number[];
                          const rank = allScores.filter((score: number) => score > userEPS).length + 1;
                          const avgScore = allScores.reduce((a: number, b: number) => a + b, 0) / allScores.length;
                          const percentile = ((10 - rank + 1) / 10 * 100).toFixed(0);
                          
                          // Get CPS (final cumulative power score)
                          const cpsData = match.analysis.charts?.powerScoreTimeline?.data?.datasets?.find(
                            (ds: any) => ds.label?.includes(userChampion)
                          );
                          const finalCPS = cpsData?.data?.[cpsData.data.length - 1] || 0;
                          
                          let performance = '';
                          if (rank === 1) performance = '🏆 MVP Performance!';
                          else if (rank <= 3) performance = '⭐ Excellent Performance';
                          else if (rank <= 5) performance = '✓ Solid Performance';
                          else if (rank <= 7) performance = '→ Average Performance';
                          else performance = '↓ Room for Improvement';
                          
                          return (
                            <div className={styles.performanceContent}>
                              <div className={styles.performanceBadge}>{performance}</div>
                              
                              {/* Basic Stats */}
                              {userParticipant && (
                                <div className={styles.basicStats}>
                                  <div className={styles.statGroup}>
                                    <span className={styles.statLabel}>KDA</span>
                                    <span className={styles.statValue}>
                                      {userParticipant.kills}/{userParticipant.deaths}/{userParticipant.assists}
                                      <span className={styles.statSubtext}>
                                        ({((userParticipant.kills + userParticipant.assists) / Math.max(1, userParticipant.deaths)).toFixed(2)} ratio)
                                      </span>
                                    </span>
                                  </div>
                                  <div className={styles.statGroup}>
                                    <span className={styles.statLabel}>CS</span>
                                    <span className={styles.statValue}>
                                      {userParticipant.totalMinionsKilled + userParticipant.neutralMinionsKilled}
                                      <span className={styles.statSubtext}>
                                        ({((userParticipant.totalMinionsKilled + userParticipant.neutralMinionsKilled) / (match.match_data.info.gameDuration / 60)).toFixed(1)} per min)
                                      </span>
                                    </span>
                                  </div>
                                  <div className={styles.statGroup}>
                                    <span className={styles.statLabel}>Gold</span>
                                    <span className={styles.statValue}>
                                      {(userParticipant.goldEarned / 1000).toFixed(1)}k
                                      <span className={styles.statSubtext}>
                                        ({(userParticipant.goldEarned / (match.match_data.info.gameDuration / 60)).toFixed(0)} per min)
                                      </span>
                                    </span>
                                  </div>
                                  <div className={styles.statGroup}>
                                    <span className={styles.statLabel}>Damage</span>
                                    <span className={styles.statValue}>
                                      {(userParticipant.totalDamageDealtToChampions / 1000).toFixed(1)}k
                                      <span className={styles.statSubtext}>
                                        ({(userParticipant.totalDamageDealtToChampions / (match.match_data.info.gameDuration / 60)).toFixed(0)} per min)
                                      </span>
                                    </span>
                                  </div>
                                </div>
                              )}
                              
                              {/* Performance Metrics */}
                              <div className={styles.performanceStats}>
                                <div className={styles.statItem}>
                                  <span className={styles.statLabel}>Match Rank</span>
                                  <span className={styles.statValue}>#{rank} of 10</span>
                                </div>
                                <div className={styles.statItem}>
                                  <span className={styles.statLabel}>EPS Score</span>
                                  <span className={styles.statValue}>{userEPS?.toFixed(1) || 'N/A'}</span>
                                </div>
                                <div className={styles.statItem}>
                                  <span className={styles.statLabel}>Final CPS</span>
                                  <span className={styles.statValue}>{finalCPS?.toFixed(1) || 'N/A'}</span>
                                </div>
                                <div className={styles.statItem}>
                                  <span className={styles.statLabel}>vs Average</span>
                                  <span className={`${styles.statValue} ${userEPS > avgScore ? styles.positive : styles.negative}`}>
                                    {userEPS > avgScore ? '+' : ''}{((userEPS - avgScore) / avgScore * 100).toFixed(1)}%
                                  </span>
                                </div>
                                {userParticipant && (
                                  <div className={styles.statItem}>
                                    <span className={styles.statLabel}>Vision Score</span>
                                    <span className={styles.statValue}>{userParticipant.visionScore}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* All Players Ranking */}
                    {match.analysis.rawStats?.epsScores && match.match_data?.info?.participants && (
                      <div className={styles.playersRanking}>
                        <h3>All Players Performance</h3>
                        <div className={styles.rankingList}>
                          {(() => {
                            const epsScores = match.analysis.rawStats.epsScores;
                            const participants = match.match_data.info.participants;
                            
                            // Create array of player data with scores
                            const playerData = participants.map((p: any) => {
                              const championName = p.championName;
                              const epsScore = epsScores[championName] || 0;
                              
                              // Get final CPS
                              const cpsData = match.analysis.charts?.powerScoreTimeline?.data?.datasets?.find(
                                (ds: any) => ds.label?.includes(championName)
                              );
                              const finalCPS = cpsData?.data?.[cpsData.data.length - 1] || 0;
                              
                              return {
                                championName,
                                summonerName: p.summonerName || p.riotIdGameName || 'Unknown',
                                teamId: p.teamId,
                                kills: p.kills,
                                deaths: p.deaths,
                                assists: p.assists,
                                epsScore,
                                finalCPS,
                                isUser: p.puuid === summoner?.puuid
                              };
                            }).sort((a: any, b: any) => b.epsScore - a.epsScore);
                            
                            return playerData.map((player: any, index: number) => (
                              <div 
                                key={player.championName} 
                                className={`${styles.playerCard} ${player.isUser ? styles.userPlayer : ''} ${player.teamId === 100 ? styles.blueTeam : styles.redTeam}`}
                              >
                                <div className={styles.playerRank}>#{index + 1}</div>
                                <img 
                                  src={`https://ddragon.leagueoflegends.com/cdn/15.22.1/img/champion/${player.championName}.png`}
                                  alt={player.championName}
                                  className={styles.playerChampionIcon}
                                  onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.style.display = 'none';
                                  }}
                                />
                                <div className={styles.playerInfo}>
                                  <div className={styles.playerName}>{player.championName}</div>
                                  <div className={styles.playerSummoner}>{player.summonerName}</div>
                                </div>
                                <div className={styles.playerStats}>
                                  <div className={styles.playerKDA}>
                                    {player.kills}/{player.deaths}/{player.assists}
                                  </div>
                                  <div className={styles.playerKDARatio}>
                                    {((player.kills + player.assists) / Math.max(1, player.deaths)).toFixed(2)} KDA
                                  </div>
                                </div>
                                <div className={styles.playerScores}>
                                  <div className={styles.scoreItem}>
                                    <span className={styles.scoreLabel}>EPS</span>
                                    <span className={styles.scoreValue}>{player.epsScore.toFixed(1)}</span>
                                  </div>
                                  <div className={styles.scoreItem}>
                                    <span className={styles.scoreLabel}>CPS</span>
                                    <span className={styles.scoreValue}>{player.finalCPS.toFixed(1)}</span>
                                  </div>
                                </div>
                              </div>
                            ));
                          })()}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Champion Tab */}
                {activeTab === 'champion' && championTabSelection && (
                  <div className={styles.tabContent}>
                    {/* Champion Selector */}
                    <div className={styles.championSelector}>
                      <label htmlFor="championTabSelect">Select Champion:</label>
                      <select
                        id="championTabSelect"
                        value={championTabSelection}
                        onChange={(e) => setChampionTabSelection(e.target.value)}
                        className={styles.championSelect}
                      >
                        {allChampions.map((championName) => (
                          <option key={championName} value={championName}>
                            {championName}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Champion Performance Details */}
                    {(() => {
                      const participant = match.match_data?.info?.participants?.find(
                        (p: any) => p.championName === championTabSelection
                      );
                      
                      if (!participant) {
                        return <p className={styles.noData}>Champion data not available</p>;
                      }

                      const epsScore = match.analysis.rawStats?.epsScores?.[championTabSelection] || 0;
                      const allScores = Object.values(match.analysis.rawStats?.epsScores || {}) as number[];
                      const rank = allScores.filter((score: number) => score > epsScore).length + 1;
                      const avgScore = allScores.reduce((a: number, b: number) => a + b, 0) / allScores.length;
                      
                      // Get final CPS
                      const cpsData = match.analysis.charts?.powerScoreTimeline?.data?.datasets?.find(
                        (ds: any) => ds.label?.includes(championTabSelection)
                      );
                      const finalCPS = cpsData?.data?.[cpsData.data.length - 1] || 0;

                      return (
                        <div className={styles.championDetails}>
                          {/* Champion Header */}
                          <div className={styles.championHeader}>
                            <img 
                              src={`https://ddragon.leagueoflegends.com/cdn/15.22.1/img/champion/${championTabSelection}.png`}
                              alt={championTabSelection}
                              className={styles.championDetailIcon}
                              onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.style.display = 'none';
                              }}
                            />
                            <div className={styles.championHeaderInfo}>
                              <h2>{championTabSelection}</h2>
                              <p className={styles.summonerName}>{participant.summonerName || participant.riotIdGameName || 'Unknown'}</p>
                              <div className={styles.championRank}>
                                Rank #{rank} of 10
                              </div>
                            </div>
                          </div>

                          {/* Stats Grid */}
                          <div className={styles.statsContainer}>
                            <h3 className={styles.statsHeader}>Basic Stats</h3>
                            <div className={styles.championStatsGrid}>
                              <div className={styles.statCard}>
                                <h4>Combat</h4>
                              <div className={styles.statRow}>
                                <span>KDA:</span>
                                <span>{participant.kills}/{participant.deaths}/{participant.assists}</span>
                              </div>
                              <div className={styles.statRow}>
                                <span>KDA Ratio:</span>
                                <span>{((participant.kills + participant.assists) / Math.max(1, participant.deaths)).toFixed(2)}</span>
                              </div>
                              <div className={styles.statRow}>
                                <span>Damage Dealt:</span>
                                <span>{(participant.totalDamageDealtToChampions / 1000).toFixed(1)}k</span>
                              </div>
                              <div className={styles.statRow}>
                                <span>Damage Taken:</span>
                                <span>{(participant.totalDamageTaken / 1000).toFixed(1)}k</span>
                              </div>
                            </div>

                            <div className={styles.statCard}>
                              <h4>Economy</h4>
                              <div className={styles.statRow}>
                                <span>Gold Earned:</span>
                                <span>{(participant.goldEarned / 1000).toFixed(1)}k</span>
                              </div>
                              <div className={styles.statRow}>
                                <span>CS:</span>
                                <span>{participant.totalMinionsKilled + participant.neutralMinionsKilled}</span>
                              </div>
                              <div className={styles.statRow}>
                                <span>CS/min:</span>
                                <span>{((participant.totalMinionsKilled + participant.neutralMinionsKilled) / (match.match_data.info.gameDuration / 60)).toFixed(1)}</span>
                              </div>
                              <div className={styles.statRow}>
                                <span>Gold/min:</span>
                                <span>{(participant.goldEarned / (match.match_data.info.gameDuration / 60)).toFixed(0)}</span>
                              </div>
                            </div>

                            <div className={styles.statCard}>
                                <h4>Vision & Objectives</h4>
                                <div className={styles.statRow}>
                                  <span>Vision Score:</span>
                                  <span>{participant.visionScore}</span>
                                </div>
                                <div className={styles.statRow}>
                                  <span>Wards Placed:</span>
                                  <span>{participant.wardsPlaced}</span>
                                </div>
                                <div className={styles.statRow}>
                                  <span>Wards Killed:</span>
                                  <span>{participant.wardsKilled}</span>
                                </div>
                                <div className={styles.statRow}>
                                  <span>Control Wards:</span>
                                  <span>{participant.visionWardsBoughtInGame}</span>
                                </div>
                              </div>
                            </div>

                            <h3 className={styles.statsHeader}>Performance Metrics</h3>
                            <div className={styles.championStatsGrid}>
                              <div className={styles.statCard}>
                                <h4>EPS Score</h4>
                                <div className={styles.statRow}>
                                  <span>Score:</span>
                                  <span className={styles.highlightValue}>{epsScore.toFixed(1)}</span>
                                </div>
                                <div className={styles.statRow}>
                                  <span>Match Rank:</span>
                                  <span>#{rank} of 10</span>
                                </div>
                                <div className={styles.statRow}>
                                  <span>vs Average:</span>
                                  <span className={epsScore > avgScore ? styles.positive : styles.negative}>
                                    {epsScore > avgScore ? '+' : ''}{((epsScore - avgScore) / avgScore * 100).toFixed(1)}%
                                  </span>
                                </div>
                              </div>

                              <div className={styles.statCard}>
                                <h4>Cumulative Power Score</h4>
                                <div className={styles.statRow}>
                                  <span>Final CPS:</span>
                                  <span className={styles.highlightValue}>{finalCPS.toFixed(1)}</span>
                                </div>
                                <div className={styles.statRowIndented}>
                                  <span>Economic (45%):</span>
                                  <span>{(finalCPS * 0.45).toFixed(1)}</span>
                                </div>
                                <div className={styles.statRowIndented}>
                                  <span>Offensive (35%):</span>
                                  <span>{(finalCPS * 0.35).toFixed(1)}</span>
                                </div>
                                <div className={styles.statRowIndented}>
                                  <span>Defensive (20%):</span>
                                  <span>{(finalCPS * 0.20).toFixed(1)}</span>
                                </div>
                              </div>

                              <div className={styles.statCard}>
                                <h4>Gold Efficiency</h4>
                                <div className={styles.statRow}>
                                  <span>Gold Earned:</span>
                                  <span>{(participant.goldEarned / 1000).toFixed(1)}k</span>
                                </div>
                                <div className={styles.statRow}>
                                  <span>Gold/min:</span>
                                  <span>{(participant.goldEarned / (match.match_data.info.gameDuration / 60)).toFixed(0)}</span>
                                </div>
                                <div className={styles.statRow}>
                                  <span>Efficiency:</span>
                                  <span>{(() => {
                                    const goldEffData = match.analysis.charts?.goldEfficiency?.data?.datasets?.[0];
                                    const labels = match.analysis.charts?.goldEfficiency?.data?.labels;
                                    const champIndex = labels?.findIndex((l: string) => l.includes(championTabSelection));
                                    const efficiency = champIndex !== -1 ? goldEffData?.data?.[champIndex] : null;
                                    return efficiency ? `${efficiency.toFixed(1)}%` : 'N/A';
                                  })()}</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Champion Graphs - Side by Side */}
                          <div className={styles.championGraphsContainer}>
                            {/* Champion PRT Graph */}
                            <div className={styles.championGraph}>
                              <h3>Power Ranking Timeline</h3>
                              <p className={styles.chartNote}>
                                Performance ranking (0-100 percentile) over time
                              </p>
                              <MatchAnalysisChart 
                                key={`champion-prt-${championTabSelection}`}
                                chartConfig={(() => {
                                  // Filter chart to show only the selected champion
                                  const chartConfig = match.analysis.charts?.powerRankingTimeline;
                                  if (!chartConfig) return chartConfig;
                                  
                                  const filtered = JSON.parse(JSON.stringify(chartConfig));
                                  
                                  if (filtered.data && filtered.data.datasets) {
                                    filtered.data.datasets = filtered.data.datasets.map((dataset: any) => {
                                      const label = dataset.label || '';
                                      const labelName = label.includes(' (') ? label.split(' (')[0].trim() : label.trim();
                                      const isSelected = labelName === championTabSelection;
                                      
                                      const addTransparency = (color: string | undefined, opacity: number) => {
                                        if (!color || typeof color !== 'string') return color;
                                        if (color.startsWith('rgb(') && !color.startsWith('rgba(')) {
                                          return color.replace('rgb(', 'rgba(').replace(')', `, ${opacity})`);
                                        }
                                        if (color.startsWith('rgba(')) {
                                          return color.replace(/[\d.]+\)$/g, `${opacity})`);
                                        }
                                        return color + Math.round(opacity * 255).toString(16).padStart(2, '0');
                                      };
                                      
                                      return {
                                        ...dataset,
                                        borderWidth: isSelected ? 4 : 1.5,
                                        borderColor: isSelected 
                                          ? dataset.borderColor 
                                          : addTransparency(dataset.borderColor, 0.2),
                                        backgroundColor: isSelected
                                          ? dataset.backgroundColor
                                          : addTransparency(dataset.backgroundColor, 0.2),
                                      };
                                    });
                                  }
                                  
                                  return filtered;
                                })()}
                                title={`${championTabSelection} Power Ranking`}
                                skipThemeColors={true}
                                height={400}
                              />
                            </div>

                            {/* Champion CPS Graph */}
                            <div className={styles.championGraph}>
                              <h3>Cumulative Power Score</h3>
                              <p className={styles.chartNote}>
                                Total accumulated combat power over time
                              </p>
                              <MatchAnalysisChart 
                                key={`champion-cps-${championTabSelection}`}
                                chartConfig={(() => {
                                  // Filter chart to show only the selected champion
                                  const chartConfig = match.analysis.charts?.powerScoreTimeline;
                                  if (!chartConfig) return chartConfig;
                                  
                                  const filtered = JSON.parse(JSON.stringify(chartConfig));
                                  
                                  if (filtered.data && filtered.data.datasets) {
                                    filtered.data.datasets = filtered.data.datasets.map((dataset: any) => {
                                      const label = dataset.label || '';
                                      const labelName = label.includes(' (') ? label.split(' (')[0].trim() : label.trim();
                                      const isSelected = labelName === championTabSelection;
                                      
                                      const addTransparency = (color: string | undefined, opacity: number) => {
                                        if (!color || typeof color !== 'string') return color;
                                        if (color.startsWith('rgb(') && !color.startsWith('rgba(')) {
                                          return color.replace('rgb(', 'rgba(').replace(')', `, ${opacity})`);
                                        }
                                        if (color.startsWith('rgba(')) {
                                          return color.replace(/[\d.]+\)$/g, `${opacity})`);
                                        }
                                        return color + Math.round(opacity * 255).toString(16).padStart(2, '0');
                                      };
                                      
                                      return {
                                        ...dataset,
                                        borderWidth: isSelected ? 4 : 1.5,
                                        borderColor: isSelected 
                                          ? dataset.borderColor 
                                          : addTransparency(dataset.borderColor, 0.2),
                                        backgroundColor: isSelected
                                          ? dataset.backgroundColor
                                          : addTransparency(dataset.backgroundColor, 0.2),
                                      };
                                    });
                                  }
                                  
                                  return filtered;
                                })()}
                                title={`${championTabSelection} Cumulative Power`}
                                skipThemeColors={true}
                                height={400}
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                )}

                {/* Statistics Tab */}
                {activeTab === 'statistics' && (
                  <div className={styles.tabContent}>
                    <div className={styles.analysisContent}>
                      <div className={styles.analysisSection}>
                        <h3>EPS Breakdown</h3>
                        <p className={styles.chartNote}>
                          End-of-Game Performance Score (Combat 40% + Economic 30% + Objective 30%)
                        </p>
                        <MatchAnalysisChart 
                          chartConfig={match.analysis.charts?.epsBreakdown}
                          title="Player Performance Breakdown"
                          enableLegendClick={true}
                        />
                      </div>

                      <div className={styles.analysisSection}>
                        <h3>Gold Efficiency</h3>
                        <p className={styles.chartNote}>
                          Power per 1000 gold spent (100% = match average)
                        </p>
                        <MatchAnalysisChart 
                          chartConfig={match.analysis.charts?.goldEfficiency}
                          title="Gold Efficiency Comparison"
                        />
                      </div>

                      {/* Champion Filter */}
                      <div className={styles.filterSection}>
                        <label htmlFor="championFilter" className={styles.filterLabel}>
                          Filter by Champion:
                        </label>
                        <select
                          id="championFilter"
                          value={selectedChampion}
                          onChange={(e) => setSelectedChampion(e.target.value)}
                          className={styles.championSelect}
                        >
                          <option value="all">All Champions</option>
                          {allChampions.map((championName) => (
                            <option key={championName} value={championName}>
                              {championName}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className={styles.analysisSection}>
                        <h3>Power Ranking Timeline</h3>
                        <p className={styles.chartNote}>
                          Relative performance ranking (0-100 percentile) at each moment in the game
                        </p>
                        <MatchAnalysisChart 
                          key={`ranking-${selectedChampion}`}
                          chartConfig={filterChartData(match.analysis.charts?.powerRankingTimeline, 'line')}
                          title="Power Ranking Over Time"
                          skipThemeColors={selectedChampion !== 'all'}
                        />
                      </div>

                      <div className={styles.analysisSection}>
                        <h3>Cumulative Power Score Timeline</h3>
                        <p className={styles.chartNote}>
                          Total accumulated combat power over time (Economic 45% + Offensive 35% + Defensive 20%)
                        </p>
                        <MatchAnalysisChart 
                          key={`power-${selectedChampion}`}
                          chartConfig={filterChartData(match.analysis.charts?.powerScoreTimeline, 'line')}
                          title="Cumulative Power Score Over Time"
                          skipThemeColors={selectedChampion !== 'all'}
                          height={700}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className={styles.analysisInfo}>
                <h2>Match Analysis</h2>
                <p className={styles.noData}>
                  Analysis not available for this match. Analysis is generated when both match and timeline data are present.
                </p>
              </div>
            )}

            {/* Info Modal */}
            {showInfoModal && (
              <div className={styles.modalOverlay} onClick={() => setShowInfoModal(false)}>
                <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                  <div className={styles.modalHeader}>
                    <h2>Metrics Explained</h2>
                    <button onClick={() => setShowInfoModal(false)} className={styles.modalClose}>×</button>
                  </div>
                  <div className={styles.modalBody}>
                    <section className={styles.metricSection}>
                      <h3>Basic Metrics</h3>
                      <div className={styles.metricItem}>
                        <strong>KDA (Kills/Deaths/Assists):</strong> Standard League of Legends combat statistics.
                      </div>
                      <div className={styles.metricItem}>
                        <strong>CS (Creep Score):</strong> Total minions and neutral monsters killed.
                      </div>
                      <div className={styles.metricItem}>
                        <strong>Gold Earned:</strong> Total gold accumulated during the match.
                      </div>
                      <div className={styles.metricItem}>
                        <strong>Vision Score:</strong> Riot's metric for vision control contribution.
                      </div>
                    </section>

                    <section className={styles.metricSection}>
                      <h3>Performance Metrics</h3>
                      
                      <div className={styles.metricItem}>
                        <strong>EPS (End-Game Performance Score):</strong>
                        <p>A comprehensive score calculated at the end of the match based on:</p>
                        <ul>
                          <li><strong>Combat (40%):</strong> KDA, damage dealt, damage taken</li>
                          <li><strong>Economic (30%):</strong> Gold earned, CS, gold efficiency</li>
                          <li><strong>Objective (30%):</strong> Turret damage, objective participation</li>
                        </ul>
                        <p>Higher EPS indicates better overall performance in the match.</p>
                      </div>

                      <div className={styles.metricItem}>
                        <strong>CPS (Cumulative Power Score):</strong>
                        <p>Tracks accumulated combat power throughout the game based on:</p>
                        <ul>
                          <li><strong>Economic (45%):</strong> Gold and experience advantages</li>
                          <li><strong>Offensive (35%):</strong> Damage output and kills</li>
                          <li><strong>Defensive (20%):</strong> Survivability and damage mitigation</li>
                        </ul>
                        <p>Shows how a player's power grows over time during the match.</p>
                      </div>

                      <div className={styles.metricItem}>
                        <strong>PRT (Power Ranking Timeline):</strong>
                        <p>Percentile ranking (0-100) showing relative performance compared to all players at each moment in the game. A value of 100 means the player was performing better than everyone else at that time.</p>
                      </div>

                      <div className={styles.metricItem}>
                        <strong>Gold Efficiency:</strong>
                        <p>Measures power gained per 1000 gold spent, normalized to match average (100%). Values above 100% indicate efficient gold usage.</p>
                      </div>
                    </section>

                    <section className={styles.metricSection}>
                      <h3>Match Rank</h3>
                      <div className={styles.metricItem}>
                        <p>Your overall placement (#1-10) among all players in the match based on EPS score.</p>
                      </div>
                    </section>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className={styles.notFound}>
            <h2>Match not found</h2>
            <button onClick={() => navigate(ROUTES.GAMES)}>Back to Games</button>
          </div>
        )}

        {/* Generate Analysis Button */}
        {match && (
          <GenerateAnalysisButton 
            onGenerate={handleGenerateAnalysis}
            onOpenFullAnalysis={handleOpenFullAnalysis}
            cachedAnalysis={cachedAnalysis}
          />
        )}

        {/* Heimerdinger Analysis Modal */}
        {analysisData && (
          <HeimerdingerModal
            isOpen={showAnalysisModal}
            onClose={() => setShowAnalysisModal(false)}
            summary={analysisData.summary}
            fullAnalysis={analysisData.fullAnalysis}
            title="Match Analysis"
          />
        )}
      </div>
    </>
  );
}

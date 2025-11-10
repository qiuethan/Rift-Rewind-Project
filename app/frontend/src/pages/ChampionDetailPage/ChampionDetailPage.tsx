import { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import styles from './ChampionDetailPage.module.css';
import { Navbar, Button, Card, Spinner } from '@/components';
import { authActions } from '@/actions/auth';
import { championProgressActions } from '@/actions/championProgress';
import { ROUTES } from '@/config';
import { useSummoner, useTheme } from '@/contexts';
import { getChampionKey, getChampionIconUrl } from '@/constants';
import type { ChampionProgressResponse } from '@/api/championProgress';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function ChampionDetailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { championName } = useParams<{ championName: string }>();
  const { summoner } = useSummoner();
  const { setTheme } = useTheme();
  const [user, setUser] = useState<any>(null);
  const [championProgress, setChampionProgress] = useState<ChampionProgressResponse | null>(null);
  const [loadingProgress, setLoadingProgress] = useState(true);
  const [progressError, setProgressError] = useState<string | null>(null);

  // Find champion from summoner's mastery data
  const champion = summoner?.champion_masteries?.find((c: any) => {
    const championId = c.championId || c.champion_id;
    const name = getChampionKey(championId);
    return name.toLowerCase() === championName?.toLowerCase();
  });

  const championId = champion ? (champion.championId || champion.champion_id) : 0;
  const championKey = getChampionKey(championId);
  const masteryLevel = champion ? (champion.championLevel || champion.champion_level || 0) : 0;
  const masteryPoints = champion ? (champion.championPoints || champion.champion_points || 0) : 0;

  // Map champion to region theme
  const getChampionTheme = (championKey: string): string => {
    const championThemeMap: { [key: string]: string } = {
      // Piltover & Zaun
      'Caitlyn': 'piltover', 'Vi': 'piltover', 'Jayce': 'piltover', 'Heimerdinger': 'piltover',
      'Ekko': 'piltover', 'Jinx': 'piltover', 'Blitzcrank': 'piltover', 'Orianna': 'piltover',
      'Camille': 'piltover', 'Zeri': 'piltover', 'Renata': 'piltover',
      // Ionia
      'Ahri': 'ionia', 'Akali': 'ionia', 'Irelia': 'ionia', 'Yasuo': 'ionia', 'Yone': 'ionia',
      'Karma': 'ionia', 'Shen': 'ionia', 'Zed': 'ionia', 'Kennen': 'ionia', 'MasterYi': 'ionia',
      'Jhin': 'ionia', 'Kayn': 'ionia', 'Xayah': 'ionia', 'Rakan': 'ionia', 'Sett': 'ionia',
      // Demacia
      'Garen': 'demacia', 'Lux': 'demacia', 'Jarvan': 'demacia', 'Fiora': 'demacia',
      'Vayne': 'demacia', 'Quinn': 'demacia', 'Shyvana': 'demacia', 'Poppy': 'demacia',
      'Galio': 'demacia', 'Lucian': 'demacia', 'Sona': 'demacia', 'Xin': 'demacia',
      // Noxus
      'Darius': 'noxus', 'Draven': 'noxus', 'Katarina': 'noxus', 'Talon': 'noxus',
      'Swain': 'noxus', 'Vladimir': 'noxus', 'Cassiopeia': 'noxus', 'Sion': 'noxus',
      'Kled': 'noxus', 'Samira': 'noxus', 'Rell': 'noxus',
      // Freljord
      'Ashe': 'freljord', 'Sejuani': 'freljord', 'Braum': 'freljord', 'Anivia': 'freljord',
      'Lissandra': 'freljord', 'Trundle': 'freljord', 'Volibear': 'freljord', 'Nunu': 'freljord',
      'Olaf': 'freljord', 'Gragas': 'freljord', 'Ornn': 'freljord',
      // Shadow Isles
      'Thresh': 'shadowIsles', 'Hecarim': 'shadowIsles', 'Kalista': 'shadowIsles',
      'Viego': 'shadowIsles', 'Gwen': 'shadowIsles', 'Elise': 'shadowIsles',
      'Maokai': 'shadowIsles', 'Yorick': 'shadowIsles', 'Karthus': 'shadowIsles',
      // Targon
      'Leona': 'targon', 'Diana': 'targon', 'Pantheon': 'targon', 'Taric': 'targon',
      'Aurelion': 'targon', 'Zoe': 'targon', 'Soraka': 'targon', 'Aphelios': 'targon',
      // Shurima
      'Azir': 'shurima', 'Nasus': 'shurima', 'Renekton': 'shurima', 'Sivir': 'shurima',
      'Xerath': 'shurima', 'Taliyah': 'shurima', 'Rammus': 'shurima', 'Amumu': 'shurima',
      'Skarner': 'shurima',
      // Bilgewater
      'MissFortune': 'bilgewater', 'Gangplank': 'bilgewater', 'Pyke': 'bilgewater',
      'Nautilus': 'bilgewater', 'Fizz': 'bilgewater', 'TwistedFate': 'bilgewater',
      'Graves': 'bilgewater', 'Illaoi': 'bilgewater', 'Nilah': 'bilgewater',
      // Void
      'Kassadin': 'void', 'Malzahar': 'void', 'KhaZix': 'void', 'RekSai': 'void',
      'Velkoz': 'void', 'ChoGath': 'void', 'KogMaw': 'void', 'Kaisa': 'void', 'BelVeth': 'void',
    };
    return championThemeMap[championKey] || 'piltover';
  };

  // Set theme based on champion
  useEffect(() => {
    if (championKey) {
      const themeId = getChampionTheme(championKey);
      setTheme(themeId);
    }
  }, [championKey, setTheme]);

  useEffect(() => {
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }
    const userData = authActions.getCurrentUser();
    setUser(userData);
  }, [navigate]);

  // Handle browser back button when coming from dashboard
  useEffect(() => {
    const handlePopState = () => {
      if (location.state?.from === 'dashboard') {
        navigate(ROUTES.DASHBOARD, { replace: true });
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [location.state, navigate]);

  return (
    <>
      <Navbar user={user} summoner={summoner} />
      <div className={styles.container}>
        {/* Back Button */}
        <Button 
          variant="secondary" 
          onClick={() => {
            const cameFromDashboard = location.state?.from === 'dashboard';
            navigate(cameFromDashboard ? ROUTES.DASHBOARD : ROUTES.CHAMPIONS);
          }} 
          className={styles.backButton}
        >
          ← Back to {location.state?.from === 'dashboard' ? 'Dashboard' : 'Champions'}
        </Button>

        {/* Champion Title Card */}
        <div className={styles.titleCard}>
          <div className={styles.championIconWrapper}>
            <img 
              src={getChampionIconUrl(championKey)} 
              alt={championKey}
              className={styles.championIcon}
            />
            <div className={styles.masteryBadge}>
              <span className={styles.badgeLabel}>LEVEL</span>
              <span className={styles.badgeValue}>{masteryLevel}</span>
            </div>
          </div>
          
          <div className={styles.championInfo}>
            <h1 className={styles.championName}>{championKey}</h1>
            <div className={styles.masteryInfo}>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Mastery Points</span>
                <span className={styles.infoValue}>{masteryPoints.toLocaleString()}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Mastery Level</span>
                <span className={styles.infoValue}>{masteryLevel}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Champion Progress */}
        {loadingProgress ? (
          <Card title="Performance Statistics">
            <div className={styles.loading}>
              <Spinner />
              <span>Loading performance data...</span>
            </div>
          </Card>
        ) : championProgress ? (
          <>
            <div className={styles.statsGrid}>
              <Card title="Performance Stats">
                <div className={styles.statsContent}>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Total Games</span>
                    <span className={styles.statValue}>{championProgress.trend.total_games}</span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Win Rate</span>
                    <span className={styles.statValue}>{championProgress.trend.win_rate.toFixed(1)}%</span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Avg EPS</span>
                    <span className={styles.statValue}>{championProgress.trend.avg_eps_score.toFixed(1)}</span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Avg KDA</span>
                    <span className={styles.statValue}>{championProgress.trend.avg_kda.toFixed(2)}</span>
                  </div>
                </div>
              </Card>

              <Card title="Performance Trends">
                <div className={styles.trendCard}>
                  <div className={styles.trendsContainer}>
                    <div className={styles.trendSection}>
                      <h4 className={styles.trendTitle}>Champion Mastery (EPS)</h4>
                      <div className={styles.trendBadge} data-trend={championProgress.trend.eps_trend > 1 ? 'improving' : championProgress.trend.eps_trend < -1 ? 'declining' : 'stable'}>
                        {championProgress.trend.eps_trend > 1 && `📈 +${championProgress.trend.eps_trend.toFixed(1)}% per game`}
                        {championProgress.trend.eps_trend < -1 && `📉 ${championProgress.trend.eps_trend.toFixed(1)}% per game`}
                        {championProgress.trend.eps_trend >= -1 && championProgress.trend.eps_trend <= 1 && `➡️ ${championProgress.trend.eps_trend.toFixed(1)}% per game`}
                      </div>
                      <p className={styles.trendDescription}>
                        Overall performance: combat, economy, objectives
                      </p>
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Avg EPS</span>
                        <span className={styles.statValue}>{championProgress.trend.avg_eps_score.toFixed(1)}</span>
                      </div>
                    </div>

                    <div className={styles.trendDivider}></div>

                    <div className={styles.trendSection}>
                      <h4 className={styles.trendTitle}>Scaling Ability (CPS)</h4>
                      <div className={styles.trendBadge} data-trend={championProgress.trend.cps_trend > 1 ? 'improving' : championProgress.trend.cps_trend < -1 ? 'declining' : 'stable'}>
                        {championProgress.trend.cps_trend > 1 && `📈 +${championProgress.trend.cps_trend.toFixed(1)}% per game`}
                        {championProgress.trend.cps_trend < -1 && `📉 ${championProgress.trend.cps_trend.toFixed(1)}% per game`}
                        {championProgress.trend.cps_trend >= -1 && championProgress.trend.cps_trend <= 1 && `➡️ ${championProgress.trend.cps_trend.toFixed(1)}% per game`}
                      </div>
                      <p className={styles.trendDescription}>
                        Power growth: gold/exp advantages, damage output
                      </p>
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Avg CPS</span>
                        <span className={styles.statValue}>{championProgress.trend.avg_cps_score.toFixed(0)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>

            {(() => {
              const history = championProgress.performance_summary?.history || [];
              if (history.length > 1) {
                return (
                  <div className={styles.chartSection}>
                    <Card title="Performance Over Time">
                      <div className={styles.chartContainer}>
                      {(() => {

                  // Get computed CSS variables for proper colors
                  const rootStyles = getComputedStyle(document.documentElement);
                  const textColor = rootStyles.getPropertyValue('--region-text').trim() || '#E9E6E1';
                  const textSecondaryColor = rootStyles.getPropertyValue('--region-text-secondary').trim() || '#B8B5B0';
                  const primaryColor = rootStyles.getPropertyValue('--region-primary').trim() || '#F5C96A';
                  const accentColor = rootStyles.getPropertyValue('--region-accent').trim() || '#55F2CE';
                  
                  // Get theme ID for theme-specific colors
                  const themeId = document.documentElement.getAttribute('data-region-theme') || 'piltover';
                  
                  // Define high-contrast colors for each theme
                  const getThemeGraphColors = (theme: string) => {
                    const colorMap: { [key: string]: { eps: string; cps: string } } = {
                      demacia: { eps: 'rgb(255, 215, 0)', cps: 'rgb(135, 206, 250)' },  // Gold & Sky Blue
                      piltover: { eps: 'rgb(99, 102, 241)', cps: 'rgb(168, 85, 247)' },
                      ionia: { eps: 'rgb(233, 167, 255)', cps: 'rgb(107, 247, 167)' },
                      noxus: { eps: 'rgb(248, 72, 72)', cps: 'rgb(177, 157, 104)' },
                      freljord: { eps: 'rgb(92, 214, 255)', cps: 'rgb(224, 251, 255)' },
                      shadowIsles: { eps: 'rgb(16, 185, 129)', cps: 'rgb(139, 92, 246)' },
                      targon: { eps: 'rgb(251, 191, 36)', cps: 'rgb(147, 197, 253)' },
                      shurima: { eps: 'rgb(251, 191, 36)', cps: 'rgb(234, 179, 8)' },
                      bilgewater: { eps: 'rgb(34, 197, 94)', cps: 'rgb(249, 115, 22)' },
                      void: { eps: 'rgb(168, 85, 247)', cps: 'rgb(236, 72, 153)' },
                    };
                    return colorMap[theme] || colorMap.piltover;
                  };
                  
                  const graphColors = getThemeGraphColors(themeId);

                  const chartData = {
                    labels: history.map((_: any, idx: number) => `Game ${idx + 1}`),
                    datasets: [
                      {
                        label: 'EPS Score',
                        data: history.map((h: any) => h.eps_score),
                        borderColor: graphColors.eps,
                        backgroundColor: graphColors.eps.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y',
                      },
                      {
                        label: 'CPS Score',
                        data: history.map((h: any) => h.cps_score),
                        borderColor: graphColors.cps,
                        backgroundColor: graphColors.cps.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y1',
                      },
                    ],
                  };

                  const options = {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                      mode: 'index' as const,
                      intersect: false,
                    },
                    plugins: {
                      legend: {
                        position: 'top' as const,
                        labels: {
                          color: textColor,
                          font: { size: 13, weight: 'bold' as const },
                          usePointStyle: true,
                          padding: 15,
                        },
                      },
                      tooltip: {
                        backgroundColor: 'rgba(20, 20, 30, 0.95)',
                        titleColor: textColor,
                        bodyColor: textColor,
                        borderColor: primaryColor,
                        borderWidth: 2,
                        padding: 12,
                        displayColors: true,
                        titleFont: { size: 13, weight: 'bold' as const },
                        bodyFont: { size: 12, weight: 'bold' as const },
                      },
                    },
                    scales: {
                      y: {
                        type: 'linear' as const,
                        display: true,
                        position: 'left' as const,
                        title: {
                          display: true,
                          text: 'EPS Score',
                          color: graphColors.eps,
                          font: { size: 13, weight: 'bold' as const },
                        },
                        grid: {
                          color: graphColors.eps.replace('rgb', 'rgba').replace(')', ', 0.15)'),
                          lineWidth: 1,
                        },
                        ticks: {
                          color: graphColors.eps,
                          font: { size: 12, weight: 'bold' as const },
                        },
                      },
                      y1: {
                        type: 'linear' as const,
                        display: true,
                        position: 'right' as const,
                        title: {
                          display: true,
                          text: 'CPS Score',
                          color: graphColors.cps,
                          font: { size: 13, weight: 'bold' as const },
                        },
                        grid: {
                          drawOnChartArea: false,
                        },
                        ticks: {
                          color: graphColors.cps,
                          font: { size: 12, weight: 'bold' as const },
                        },
                      },
                      x: {
                        grid: {
                          color: 'rgba(255, 255, 255, 0.08)',
                          lineWidth: 1,
                        },
                        ticks: {
                          color: textColor,
                          font: { size: 12, weight: 'bold' as const },
                        },
                      },
                    },
                  };

                  return (
                    <div style={{ height: '350px' }}>
                      <Line data={chartData} options={options} />
                    </div>
                  );
                })()}
                      </div>
                    </Card>
                  </div>
                );
              }
              return null;
            })()}

            <Card title="Recent Matches">
              <div className={styles.matchesList}>
                {championProgress.recent_matches.length === 0 ? (
                  <p className={styles.noMatches}>No recent matches found.</p>
                ) : (
                  championProgress.recent_matches
                    .sort((a, b) => b.game_date - a.game_date)
                    .map((match) => {
                      const kdaColor = (() => {
                        const kda = match.kda;
                        if (kda >= 4) return styles.kdaExcellent;
                        if (kda >= 3) return styles.kdaGood;
                        if (kda >= 2) return styles.kdaAverage;
                        return styles.kdaPoor;
                      })();

                      const getItemIconUrl = (itemId: number) => {
                        if (itemId === 0) return null;
                        return `https://ddragon.leagueoflegends.com/cdn/15.22.1/img/item/${itemId}.png`;
                      };

                      return (
                        <div
                          key={match.match_id}
                          className={`${styles.matchCard} ${match.win ? styles.win : styles.loss}`}
                          onClick={() => navigate(`/match/${match.match_id}`)}
                        >
                          <div className={styles.matchHeader}>
                            <span className={styles.matchResult}>{match.win ? 'Victory' : 'Defeat'}</span>
                            <span className={styles.matchDate}>
                              {new Date(match.game_date * 1000).toLocaleDateString()}
                            </span>
                          </div>

                          <div className={styles.matchDetails}>
                            <div className={styles.championSection}>
                              <img
                                src={getChampionIconUrl(championKey)}
                                alt={match.champion_name}
                                className={styles.championIcon}
                              />
                              <span className={styles.championName}>{match.champion_name}</span>
                            </div>

                            <div className={styles.statsSection}>
                              <div className={styles.kda}>
                                <span className={kdaColor}>
                                  {match.kills} / {match.deaths} / {match.assists}
                                </span>
                              </div>
                              <div className={styles.stats}>
                                <span>{match.cs} CS</span>
                                <span>{(match.gold / 1000).toFixed(1)}k Gold</span>
                              </div>
                            </div>

                            <div className={styles.itemsSection}>
                              {(match.items || []).slice(0, 6).map((itemId: number, index: number) => (
                                <div key={index} className={styles.itemSlot}>
                                  {itemId !== 0 && getItemIconUrl(itemId) && (
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
                    })
                )}
              </div>
            </Card>
          </>
        ) : (
          <Card title="Performance Statistics">
            <div className={styles.noProgress}>
              <p>No recent games played with this champion.</p>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Play some matches to see your performance stats and progress!
              </p>
            </div>
          </Card>
        )}
      </div>
    </>
  );
}

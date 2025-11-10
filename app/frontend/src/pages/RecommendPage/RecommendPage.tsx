import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './RecommendPage.module.css';
import { Navbar, Spinner, Card, Modal } from '@/components';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';
import { useSummoner } from '@/contexts';
import { championsApi } from '@/api/champions';
import { getAbilityAsset } from '@/utils/abilities';
import { getChampionIconUrl, getChampionKey } from '@/constants';
import type { ChampionRecommendation, AbilitySimilarity } from '@/api/champions';

interface ChampionRecommendationWithDetails extends ChampionRecommendation {}

interface ChampionMastery {
  championId?: number;
  champion_id?: number;
  championName?: string;
}

// Separate component for recommendations card
function RecommendationsCard({ summonerId, championMasteries }: { summonerId: string; championMasteries?: ChampionMastery[] }) {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<ChampionRecommendationWithDetails[]>([]);
  const [selectedChampion, setSelectedChampion] = useState<ChampionRecommendationWithDetails | null>(null);
  const [abilitySimilarities, setAbilitySimilarities] = useState<AbilitySimilarity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch recommendations
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!summonerId) return;

      try {
        setLoading(true);
        const response = await championsApi.getRecommendations({
          summoner_id: summonerId,
          limit: 5,
          include_reasoning: true,
        });

        // Transform recommendations to include additional details if needed
        const enhancedRecommendations: ChampionRecommendationWithDetails[] = response.recommendations.map(rec => ({
          ...rec,
          // Use API-provided image URL or fallback
          champion_image_url: rec.champion_image_url || `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${rec.champion_id}_0.jpg`,
        }));

        console.log('Recommendations with tags:', enhancedRecommendations);
        setRecommendations(enhancedRecommendations);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        setError('Failed to load recommendations. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (summonerId) {
      fetchRecommendations();
    }
  }, [summonerId]);

  // Fetch ability similarities when a champion is selected
  useEffect(() => {
    const fetchAbilitySimilarities = async () => {
      if (!selectedChampion) return;

      // Add a small delay to ensure champion pool data is ready
      await new Promise(resolve => setTimeout(resolve, 500));

      try {
        const response = await championsApi.getAbilitySimilarities(selectedChampion.champion_id);
        setAbilitySimilarities(response.abilities);
      } catch (err) {
        console.error('Failed to fetch ability similarities:', err);
        setAbilitySimilarities([]);
      }
    };

    fetchAbilitySimilarities();
  }, [selectedChampion]);

  const handleChampionClick = (champion: ChampionRecommendationWithDetails) => {
    console.log('Selected champion:', champion);
    console.log('Champion tags:', champion.champion_tags);
    setSelectedChampion(champion);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedChampion(null);
    setAbilitySimilarities([]);
  };

  const hasPlayedChampion = (championName: string): boolean => {
    if (!championMasteries || championMasteries.length === 0) {
      console.log('No masteries available');
      return false;
    }
    
    // Normalize the champion name for comparison
    const normalizedSearchName = championName.toLowerCase().replace(/\s+/g, '');
    console.log('Checking if played:', championName, '(normalized:', normalizedSearchName + ')');
    
    const result = championMasteries.some(mastery => {
      const championId = mastery.championId || mastery.champion_id;
      if (!championId) return false;
      
      // Get the champion name from the ID and normalize it
      const masteryChampionName = getChampionKey(championId);
      const normalizedMasteryName = masteryChampionName.toLowerCase().replace(/\s+/g, '');
      
      if (normalizedMasteryName === normalizedSearchName) {
        console.log('Match found!', masteryChampionName, 'matches', championName);
      }
      
      return normalizedMasteryName === normalizedSearchName;
    });
    
    console.log('Has played', championName + ':', result);
    return result;
  };

  if (loading) {
    return (
      <Card className={styles.recommendationCard}>
        <div className={styles.loading}>
          <Spinner size="large" />
          <span>Loading recommendations...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={styles.recommendationCard}>
        <div className={styles.error}>
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className={styles.retryButton}>
            Try Again
          </button>
        </div>
      </Card>
    );
  }

  if (recommendations.length === 0) {
    return (
      <Card className={styles.recommendationCard}>
        <div className={styles.empty}>
          <h2>No recommendations available yet</h2>
          <p>Play some ranked games to help us understand your playstyle and provide personalized champion recommendations!</p>
          <p className={styles.emptySubtext}>The more you play, the better our recommendations become.</p>
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card className={styles.recommendationCard}>
        <div className={styles.recommendationsList}>
          {recommendations.map((champion, index) => (
            <div
              key={champion.champion_id}
              className={styles.championCard}
              onClick={() => handleChampionClick(champion)}
            >
              <div className={styles.championRank}>#{index + 1}</div>
              <img
                src={getChampionIconUrl(champion.champion_name)}
                alt={champion.champion_name}
                className={styles.championIcon}
              />
              <div className={styles.championCardInfo}>
                <h3 className={styles.championCardName}>{champion.champion_name}</h3>
                {champion.reasoning && (
                  <p className={styles.championCardReasoning}>{champion.reasoning}</p>
                )}
              </div>
              <div className={styles.championCardArrow}>→</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Modal for champion details */}
      {selectedChampion && (
        <Modal isOpen={isModalOpen} onClose={handleCloseModal} title={selectedChampion.champion_name}>
          <div className={styles.modalContent}>
            <div className={styles.modalTopSection}>
              <div className={styles.modalSplashContainer}>
                <img
                  src={`https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${selectedChampion.champion_name}_0.jpg`}
                  alt={selectedChampion.champion_name}
                  className={styles.modalSplash}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Teemo_0.jpg';
                  }}
                />
              </div>
              
              <div className={styles.modalTopInfo}>
                {selectedChampion.champion_title && (
                  <p className={styles.championTitle}>
                    {selectedChampion.champion_title}
                  </p>
                )}
                {selectedChampion.reasoning && (
                  <div className={styles.reasoningBox}>
                    <strong>Why this champion?</strong>
                    <p>{selectedChampion.reasoning}</p>
                  </div>
                )}
                
                {selectedChampion.champion_tags && selectedChampion.champion_tags.length > 0 && (
                  <div className={styles.championInfo}>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>Role:</span>
                      <span className={styles.infoValue}>{selectedChampion.champion_tags.join(', ')}</span>
                    </div>
                  </div>
                )}

                <button
                  className={styles.viewStatsButton}
                  onClick={() => {
                    if (hasPlayedChampion(selectedChampion.champion_name)) {
                      handleCloseModal();
                      navigate(`/champion/${selectedChampion.champion_name.toLowerCase()}`, { state: { from: 'recommend' } });
                    }
                  }}
                  disabled={!hasPlayedChampion(selectedChampion.champion_name)}
                >
                  {hasPlayedChampion(selectedChampion.champion_name) 
                    ? `View Your Stats on ${selectedChampion.champion_name}`
                    : 'You have not played this champion yet'
                  }
                </button>
              </div>
            </div>
            
            <div className={styles.modalBody}>

              {abilitySimilarities.length > 0 && (
                <div className={styles.abilitiesSection}>
                  <h4>Ability Comparisons</h4>
                  <div className={styles.abilityGrid}>
                    {['Q', 'W', 'E', 'R'].map((abilityType) => {
                      const ability = abilitySimilarities.find(a => a.ability_type === abilityType);
                      if (!ability) return null;

                      return (
                        <div key={abilityType} className={styles.abilityComparison}>
                          <div className={`${styles.abilityKeyBadge} ${styles[ability.ability_type]}`}>
                            {ability.ability_type}
                          </div>
                          <div className={styles.abilityHeader}>
                            <div className={styles.abilityHeaderLeft}>
                              {(() => {
                                const asset = getAbilityAsset(
                                  selectedChampion.champion_name,
                                  ability.ability_type as 'Q' | 'W' | 'E' | 'R'
                                );
                                return asset ? (
                                  <img
                                    src={asset.imageUrl}
                                    alt={`${ability.ability_name}`}
                                    className={styles.abilityIcon}
                                  />
                                ) : (
                                  <div className={`${styles.abilityIcon} ${styles[ability.ability_type]}`}>
                                    {ability.ability_type}
                                  </div>
                                );
                              })()}
                              <span className={styles.abilityName}>{ability.ability_name}</span>
                            </div>
                            
                            <div className={styles.similarityIndicator}>
                              <span className={styles.similarText}>≈</span>
                              <span className={styles.similarityScore}>{Math.round(ability.similarity_score * 100)}%</span>
                            </div>

                            <div className={styles.abilityHeaderRight}>
                              {(() => {
                                const asset = getAbilityAsset(
                                  ability.similar_champion,
                                  ability.similar_ability_type as 'Q' | 'W' | 'E' | 'R'
                                );
                                return asset ? (
                                  <img
                                    src={asset.imageUrl}
                                    alt={`${ability.similar_ability_name}`}
                                    className={styles.abilityIcon}
                                  />
                                ) : (
                                  <div className={`${styles.abilityIcon} ${styles[ability.similar_ability_type]}`}>
                                    {ability.similar_ability_type}
                                  </div>
                                );
                              })()}
                              <span className={styles.abilityName}>{ability.similar_ability_name}</span>
                            </div>
                          </div>
                          <p className={styles.explanation}>{ability.explanation}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}

export default function RecommendPage() {
  const navigate = useNavigate();
  const { summoner, loading: summonerLoading } = useSummoner();
  const [user, setUser] = useState<any>(null);

  // Check authentication
  useEffect(() => {
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }
    const userData = authActions.getCurrentUser();
    setUser(userData);
  }, [navigate]);

  // Only show loading spinner while waiting for summoner data
  if (summonerLoading) {
    return (
      <>
        <Navbar user={user} summoner={summoner} />
        <div className={styles.container}>
          <div className={styles.loading}>
            <Spinner size="large" />
            <span>Loading...</span>
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
          <button 
            className={styles.backButton}
            onClick={() => navigate(ROUTES.HOME)}
            aria-label="Back to main menu"
          >
            ← Back to Main Menu
          </button>
          <h1 className={styles.pageTitle}>Champion Recommendations</h1>
        </div>
        {summoner?.id && <RecommendationsCard summonerId={summoner.id} championMasteries={summoner.champion_masteries} />}
      </div>
    </>
  );
}

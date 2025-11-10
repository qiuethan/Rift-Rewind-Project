import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './RecommendPage.module.css';
import { Navbar, Spinner } from '@/components';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';
import { useSummoner } from '@/contexts';
import { championsApi } from '@/api/champions';
import { getAbilityAsset } from '@/utils/abilities';
import type { ChampionRecommendation, AbilitySimilarity } from '@/api/champions';

interface ChampionRecommendationWithDetails extends ChampionRecommendation {}

export default function RecommendPage() {
  const navigate = useNavigate();
  const { summoner, loading: summonerLoading } = useSummoner();
  const [user, setUser] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<ChampionRecommendationWithDetails[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [abilitySimilarities, setAbilitySimilarities] = useState<AbilitySimilarity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authentication
  useEffect(() => {
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }
    const userData = authActions.getCurrentUser();
    setUser(userData);
  }, [navigate]);

  // Fetch recommendations
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!summoner?.id) return;

      try {
        setLoading(true);
        const response = await championsApi.getRecommendations({
          summoner_id: summoner.id,
          limit: 5,
          include_reasoning: true,
        });

        // Transform recommendations to include additional details if needed
        const enhancedRecommendations: ChampionRecommendationWithDetails[] = response.recommendations.map(rec => ({
          ...rec,
          // Use API-provided image URL or fallback
          champion_image_url: rec.champion_image_url || `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${rec.champion_id}_0.jpg`,
        }));

        setRecommendations(enhancedRecommendations);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        setError('Failed to load recommendations. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (summoner?.id) {
      fetchRecommendations();
    }
  }, [summoner?.id]);

  // Fetch ability similarities when current recommendation changes
  useEffect(() => {
    const fetchAbilitySimilarities = async () => {
      if (recommendations.length === 0) return;

      const currentRecommendation = recommendations[currentIndex];
      if (!currentRecommendation) return;

      try {
        const response = await championsApi.getAbilitySimilarities(currentRecommendation.champion_id);
        setAbilitySimilarities(response.abilities);
      } catch (err) {
        console.error('Failed to fetch ability similarities:', err);
        // Don't set error state for this, just log it
      }
    };

    fetchAbilitySimilarities();
  }, [recommendations, currentIndex]);

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < recommendations.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') {
        handlePrevious();
      } else if (event.key === 'ArrowRight') {
        handleNext();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentIndex, recommendations.length]);

  if (summonerLoading || loading) {
    return (
      <>
        <Navbar user={user} summoner={summoner} />
        <div className={styles.container}>
          <div className={styles.loading}>
            <Spinner size="large" />
            <span>Loading recommendations...</span>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar user={user} summoner={summoner} />
        <div className={styles.container}>
          <div className={styles.error}>
            <h2>Oops! Something went wrong</h2>
            <p>{error}</p>
            <button onClick={() => window.location.reload()} className={styles.retryButton}>
              Try Again
            </button>
          </div>
        </div>
      </>
    );
  }

  if (recommendations.length === 0) {
    return (
      <>
        <Navbar user={user} summoner={summoner} />
        <div className={styles.container}>
          <div className={styles.empty}>
            <h2>No recommendations available yet</h2>
            <p>Play some ranked games to help us understand your playstyle and provide personalized champion recommendations!</p>
            <p className={styles.emptySubtext}>The more you play, the better our recommendations become.</p>
          </div>
        </div>
      </>
    );
  }

  const currentRecommendation = recommendations[currentIndex];

  return (
    <>
      <Navbar user={user} summoner={summoner} />
      <div className={styles.container}>
        <div className={styles.recommendationContainer} role="region" aria-label="Champion recommendations">
          {/* Navigation */}
          <nav className={styles.navigation} aria-label="Recommendation navigation">
            <button
              className={styles.navButton}
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              aria-label="Previous recommendation"
            >
              ← Back
            </button>
            <span className={styles.position} aria-live="polite">
              #{currentIndex + 1} of {recommendations.length}
            </span>
            <button
              className={styles.navButton}
              onClick={handleNext}
              disabled={currentIndex === recommendations.length - 1}
              aria-label="Next recommendation"
            >
              Next →
            </button>
          </nav>

          {/* Champion Display */}
          <section className={styles.championDisplay} aria-labelledby="champion-name">
            <div className={styles.championImage}>
              <img
                src={`https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${currentRecommendation.champion_name}_0.jpg`}
                alt={`${currentRecommendation.champion_name} splash art`}
                onError={(e) => {
                  // Fallback to default image
                  (e.target as HTMLImageElement).src = 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Teemo_0.jpg';
                }}
              />
            </div>
            <div className={styles.championInfo}>
              <h2 id="champion-name" className={styles.championName}>{currentRecommendation.champion_name}</h2>
              <p className={styles.championTitle}>
                {currentRecommendation.champion_title || 
                 (currentRecommendation.champion_tags ? currentRecommendation.champion_tags.join(', ') : 'Champion')}
              </p>
              {currentRecommendation.lore_snippet && (
                <p className={styles.loreSnippet}>{currentRecommendation.lore_snippet}</p>
              )}
              {currentRecommendation.reasoning && (
                <p className={styles.reasoning}>{currentRecommendation.reasoning}</p>
              )}
              <button 
                className={styles.learnMoreButton}
                onClick={() => navigate(`/champion/${currentRecommendation.champion_name.toLowerCase()}`)}
                aria-label={`View your stats on ${currentRecommendation.champion_name}`}
              >
                Your Stats on {currentRecommendation.champion_name}
              </button>
            </div>
          </section>

          {/* Ability Comparison Grid */}
          <section className={styles.abilityGrid} aria-labelledby="ability-comparisons">
            <div className={styles.abilityColumn}>
              {['Q', 'W'].map(abilityType => {
                const ability = abilitySimilarities.find(a => a.ability_type === abilityType);
                if (!ability) return null;
                return (
                  <div key={abilityType} className={styles.abilityComparison}>
                    <div className={styles.abilityRow}>
                      <div className={styles.abilityItem}>
                        {(() => {
                          const asset = getAbilityAsset(currentRecommendation.champion_name, ability.ability_type as 'Q' | 'W' | 'E' | 'R');
                          return asset ? (
                            <img
                              src={asset.imageUrl}
                              alt={`${currentRecommendation.champion_name} ${ability.ability_name} (${ability.ability_type})`}
                              className={styles.abilityIcon}
                              onError={(e) => {
                                // Fallback to letter icon
                                const img = e.target as HTMLImageElement;
                                img.style.display = 'none';
                                const fallback = document.createElement('div');
                                fallback.className = `${styles.abilityIcon} ${styles[ability.ability_type]}`;
                                fallback.textContent = ability.ability_type;
                                img.parentElement?.appendChild(fallback);
                              }}
                            />
                          ) : (
                            <div className={`${styles.abilityIcon} ${styles[ability.ability_type]}`}>
                              {ability.ability_type}
                            </div>
                          );
                        })()}
                        <span className={styles.abilityName}><span className={styles.championNameInAbility}>{currentRecommendation.champion_name}</span>'s {ability.ability_name} ({ability.ability_type})</span>
                      </div>
                      <div className={styles.similaritySection}>
                        <div className={styles.similarityScore}>
                          {ability.similarity_score.toFixed(2)}
                        </div>
                        <div className={styles.similarText}>is similar to</div>
                      </div>
                      <div className={styles.abilityItem}>
                        {(() => {
                          const asset = getAbilityAsset(ability.similar_champion, ability.similar_ability_type as 'Q' | 'W' | 'E' | 'R');
                          return asset ? (
                            <img
                              src={asset.imageUrl}
                              alt={`${ability.similar_champion} ${ability.similar_ability_name} (${ability.similar_ability_type})`}
                              className={styles.abilityIcon}
                              onError={(e) => {
                                // Fallback to letter icon
                                const img = e.target as HTMLImageElement;
                                img.style.display = 'none';
                                const fallback = document.createElement('div');
                                fallback.className = `${styles.abilityIcon} ${styles[ability.similar_ability_type]}`;
                                fallback.textContent = ability.similar_ability_type;
                                img.parentElement?.appendChild(fallback);
                              }}
                            />
                          ) : (
                            <div className={`${styles.abilityIcon} ${styles[ability.similar_ability_type]}`}>
                              {ability.similar_ability_type}
                            </div>
                          );
                        })()}
                        <span className={styles.abilityName}>
                          <span className={styles.championNameInAbility}>{ability.similar_champion}</span>'s {ability.similar_ability_name} ({ability.similar_ability_type})
                        </span>
                      </div>
                    </div>
                    <div className={styles.explanation} title={ability.explanation}>
                      {ability.explanation}
                    </div>
                  </div>
                );
              })}
            </div>            <div className={styles.abilityColumn}>
              {['E', 'R'].map(abilityType => {
                const ability = abilitySimilarities.find(a => a.ability_type === abilityType);
                if (!ability) return null;
                return (
                  <div key={abilityType} className={styles.abilityComparison}>
                    <div className={styles.abilityRow}>
                      <div className={styles.abilityItem}>
                        {(() => {
                          const asset = getAbilityAsset(currentRecommendation.champion_name, ability.ability_type as 'Q' | 'W' | 'E' | 'R');
                          return asset ? (
                            <img
                              src={asset.imageUrl}
                              alt={`${currentRecommendation.champion_name} ${ability.ability_name} (${ability.ability_type})`}
                              className={styles.abilityIcon}
                              onError={(e) => {
                                // Fallback to letter icon
                                const img = e.target as HTMLImageElement;
                                img.style.display = 'none';
                                const fallback = document.createElement('div');
                                fallback.className = `${styles.abilityIcon} ${styles[ability.ability_type]}`;
                                fallback.textContent = ability.ability_type;
                                img.parentElement?.appendChild(fallback);
                              }}
                            />
                          ) : (
                            <div className={`${styles.abilityIcon} ${styles[ability.ability_type]}`}>
                              {ability.ability_type}
                            </div>
                          );
                        })()}
                        <span className={styles.abilityName}><span className={styles.championNameInAbility}>{currentRecommendation.champion_name}</span>'s {ability.ability_name} ({ability.ability_type})</span>
                      </div>
                      <div className={styles.similaritySection}>
                        <div className={styles.similarityScore}>
                          {ability.similarity_score.toFixed(2)}
                        </div>
                        <div className={styles.similarText}>is similar to</div>
                      </div>
                      <div className={styles.abilityItem}>
                        {(() => {
                          const asset = getAbilityAsset(ability.similar_champion, ability.similar_ability_type as 'Q' | 'W' | 'E' | 'R');
                          return asset ? (
                            <img
                              src={asset.imageUrl}
                              alt={`${ability.similar_champion} ${ability.similar_ability_name} (${ability.similar_ability_type})`}
                              className={styles.abilityIcon}
                              onError={(e) => {
                                // Fallback to letter icon
                                const img = e.target as HTMLImageElement;
                                img.style.display = 'none';
                                const fallback = document.createElement('div');
                                fallback.className = `${styles.abilityIcon} ${styles[ability.similar_ability_type]}`;
                                fallback.textContent = ability.similar_ability_type;
                                img.parentElement?.appendChild(fallback);
                              }}
                            />
                          ) : (
                            <div className={`${styles.abilityIcon} ${styles[ability.similar_ability_type]}`}>
                              {ability.similar_ability_type}
                            </div>
                          );
                        })()}
                        <span className={styles.abilityName}>
                          <span className={styles.championNameInAbility}>{ability.similar_champion}</span>'s {ability.similar_ability_name} ({ability.similar_ability_type})
                        </span>
                      </div>
                    </div>
                    <div className={styles.explanation} title={ability.explanation}>
                      {ability.explanation}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </div>
      </div>
    </>
  );
}

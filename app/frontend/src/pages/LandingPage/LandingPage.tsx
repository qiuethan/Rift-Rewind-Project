import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './LandingPage.module.css';
import { Button, BrandHeader, PrimaryCTAGroup, SummonerLinkModal } from '@/components';
import { ROUTES } from '@/config';
import { authActions } from '@/actions/auth';
import { useSummoner } from '@/contexts';

export default function LandingPage() {
  const navigate = useNavigate();
  const { summoner, loading: summonerLoading } = useSummoner();
  const [user, setUser] = useState<any>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showSummonerLinkModal, setShowSummonerLinkModal] = useState(false);

  useEffect(() => {
    // Check if user is authenticated
    const authenticated = authActions.isAuthenticated();
    setIsAuthenticated(authenticated);
    
    if (authenticated) {
      const userData = authActions.getCurrentUser();
      setUser(userData);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && !summonerLoading && !summoner) {
      setShowSummonerLinkModal(true);
    }
  }, [isAuthenticated, summonerLoading, summoner]);

  return (
    <div className={styles.container}>
      {!isAuthenticated && (
        <>
          <div className={styles.centeredContent}>
            <div className={styles.unauthenticatedGroup}>
              <BrandHeader />
              <main className={styles.main}>
                <section className={styles.hero}>
                  <div className={styles.cta}>
                    <Button onClick={() => navigate(ROUTES.REGISTER)} fullWidth={false}>
                      Start Analyzing
                    </Button>
                    <Button variant="secondary" onClick={() => navigate(ROUTES.LOGIN)} fullWidth={false}>
                      Sign In
                    </Button>
                  </div>
                </section>
              </main>
            </div>
          </div>
          <section className={styles.features}>
            <div className={styles.feature}>
              <div className={styles.featureIcon}>
                <img 
                  src="/img/emotes/bard.png" 
                  alt="Bard" 
                  className={styles.emote}
                  onError={(e) => {
                    console.error('Failed to load bard.png');
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
              <h3 className={styles.featureTitle}>Match Analysis</h3>
              <p className={styles.featureText}>
                Deep dive into your match history with AI-powered performance insights
                and actionable recommendations.
              </p>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>
                <img 
                  src="/img/emotes/heimerdinger.png" 
                  alt="Heimerdinger" 
                  className={styles.emote}
                  onError={(e) => {
                    console.error('Failed to load heimerdinger.png');
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
              <h2 className={styles.featureTitle}> New Champions</h2>
              <p className={styles.featureText}>
                Discover champions that match your playstyle and maximize your win rate
                based on your unique strengths.
              </p>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>
                <img 
                  src="/img/emotes/leesin.png" 
                  alt="Lee Sin" 
                  className={styles.emote}
                  onError={(e) => {
                    console.error('Failed to load leesin.png');
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
              <h3 className={styles.featureTitle}>Skill Progression</h3>
              <p className={styles.featureText}>
                Track your improvement over time with detailed analytics and personalized
                training recommendations.
              </p>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>
                <img 
                  src="/img/emotes/blitzcrank.png" 
                  alt="Blitzcrank" 
                  className={styles.emote}
                  onError={(e) => {
                    console.error('Failed to load blitzcrank.png');
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
              <h3 className={styles.featureTitle}>AI Insights</h3>
              <p className={styles.featureText}>
                Get intelligent feedback on your gameplay patterns, decision-making,
                and strategic opportunities.
              </p>
            </div>
          </section>
        </>
      )}

      {isAuthenticated && summoner && (
        <div className={styles.authenticatedContainer}>
          <div className={`${styles.centeredContent} ${styles.authenticatedContent}`}>
            <div className={styles.welcomeGroup}>
              <BrandHeader/>
              <section className={styles.heroAuthenticated}>
              </section>
              <h1 className={styles.welcomeTitle}>
                  Welcome back, <span className={styles.underlinedName}>{summoner.game_name}</span>.
                </h1>
            </div>
            <PrimaryCTAGroup />
          </div>
        </div>
      )}

      {isAuthenticated && !summoner && !summonerLoading && (
        <div className={styles.container}>
          {/* Background remains */}
          <SummonerLinkModal
            isOpen={showSummonerLinkModal}
            onClose={() => setShowSummonerLinkModal(false)}
          />
        </div>
      )}
    </div>
  );
}

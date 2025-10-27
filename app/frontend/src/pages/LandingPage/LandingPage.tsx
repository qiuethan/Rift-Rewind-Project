import { useNavigate } from 'react-router-dom';
import styles from './LandingPage.module.css';
import { Button } from '@/components';
import { ROUTES } from '@/config';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <nav className={styles.nav}>
        <div className={styles.navContent}>
          <h2 className={styles.logo}>Rift Rewind</h2>
          <div className={styles.navButtons}>
            <Button variant="secondary" onClick={() => navigate(ROUTES.LOGIN)}>
              Login
            </Button>
            <Button onClick={() => navigate(ROUTES.REGISTER)}>
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      <main className={styles.main}>
        <section className={styles.hero}>
          <h1 className={styles.title}>
            Master League of Legends
            <br />
            with AI-Powered Insights
          </h1>
          <p className={styles.subtitle}>
            Analyze your gameplay, discover your perfect champions, and climb the ranks
            with personalized recommendations powered by advanced AI.
          </p>
          <div className={styles.cta}>
            <Button onClick={() => navigate(ROUTES.REGISTER)} fullWidth={false}>
              Start Analyzing
            </Button>
            <Button variant="secondary" onClick={() => navigate(ROUTES.LOGIN)} fullWidth={false}>
              Sign In
            </Button>
          </div>
        </section>

        <section className={styles.features}>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>📊</div>
            <h3 className={styles.featureTitle}>Match Analysis</h3>
            <p className={styles.featureText}>
              Deep dive into your match history with AI-powered performance insights
              and actionable recommendations.
            </p>
          </div>

          <div className={styles.feature}>
            <div className={styles.featureIcon}>🏆</div>
            <h3 className={styles.featureTitle}>Champion Recommendations</h3>
            <p className={styles.featureText}>
              Discover champions that match your playstyle and maximize your win rate
              based on your unique strengths.
            </p>
          </div>

          <div className={styles.feature}>
            <div className={styles.featureIcon}>📈</div>
            <h3 className={styles.featureTitle}>Skill Progression</h3>
            <p className={styles.featureText}>
              Track your improvement over time with detailed analytics and personalized
              training recommendations.
            </p>
          </div>

          <div className={styles.feature}>
            <div className={styles.featureIcon}>🤖</div>
            <h3 className={styles.featureTitle}>AI Insights</h3>
            <p className={styles.featureText}>
              Get intelligent feedback on your gameplay patterns, decision-making,
              and strategic opportunities.
            </p>
          </div>
        </section>

        <section className={styles.cta2}>
          <h2 className={styles.cta2Title}>Ready to level up your game?</h2>
          <p className={styles.cta2Text}>
            Join thousands of players improving their League of Legends skills with Rift Rewind.
          </p>
          <Button onClick={() => navigate(ROUTES.REGISTER)}>
            Create Free Account
          </Button>
        </section>
      </main>

      <footer className={styles.footer}>
        <p className={styles.footerText}>
          © 2025 Rift Rewind. All rights reserved.
        </p>
      </footer>
    </div>
  );
}

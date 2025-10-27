import { Card } from '@/components';
import styles from './WelcomeCard.module.css';

export default function WelcomeCard() {
  return (
    <Card title="Welcome to Rift Rewind! 🎮">
      <div className={styles.welcome}>
        <p>
          Rift Rewind is your AI-powered League of Legends analytics platform. Get personalized
          insights, champion recommendations, and performance analysis.
        </p>
        <ul className={styles.features}>
          <li>📊 Match performance analysis</li>
          <li>🏆 Champion recommendations based on your playstyle</li>
          <li>📈 Skill progression tracking</li>
          <li>🤖 AI-powered insights and tips</li>
        </ul>
      </div>
    </Card>
  );
}

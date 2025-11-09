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
          <li>
            <img 
              src="/img/emotes/bard.png" 
              alt="Bard" 
              className={styles.emote}
              onError={(e) => {
                console.error('Failed to load bard.png');
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
            Match performance analysis
          </li>
          <li>
            <img 
              src="/img/emotes/heimerdinger.png" 
              alt="Heimerdinger" 
              className={styles.emote}
              onError={(e) => {
                console.error('Failed to load heimerdinger.png');
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
            Champion recommendations based on your playstyle
          </li>
          <li>
            <img 
              src="/img/emotes/leesin.png" 
              alt="Lee Sin" 
              className={styles.emote}
              onError={(e) => {
                console.error('Failed to load leesin.png');
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
            Skill progression tracking
          </li>
          <li>
            <img 
              src="/img/emotes/blitzcrank.png" 
              alt="Blitzcrank" 
              className={styles.emote}
              onError={(e) => {
                console.error('Failed to load blitzcrank.png');
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
            AI-powered insights and tips
          </li>
        </ul>
      </div>
    </Card>
  );
}

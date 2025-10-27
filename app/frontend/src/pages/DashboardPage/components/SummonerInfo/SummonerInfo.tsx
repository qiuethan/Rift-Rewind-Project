import { Button, Card, Spinner } from '@/components';
import { getProfileIconUrl } from '@/constants';
import styles from './SummonerInfo.module.css';

interface SummonerInfoProps {
  summoner: any;
  onLinkAccount: () => void;
}

export default function SummonerInfo({ summoner, onLinkAccount }: SummonerInfoProps) {
  if (!summoner) {
    return (
      <Card title="Summoner Info">
        <div className={styles.empty}>
          <Spinner />
          <p>No summoner linked yet</p>
          <Button onClick={onLinkAccount}>Link Account</Button>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Summoner Info">
      <div className={styles.info}>
        <div className={styles.summonerHeader}>
          <img
            src={getProfileIconUrl(summoner.profile_icon_id)}
            alt="Profile Icon"
            className={styles.profileIcon}
          />
          <div className={styles.summonerDetails}>
            <div className={styles.summonerName}>{summoner.summoner_name}</div>
            <div className={styles.summonerLevel}>Level {summoner.summoner_level}</div>
          </div>
        </div>

        <div className={styles.updateButton}>
          <Button fullWidth onClick={onLinkAccount}>
            Update League Account
          </Button>
        </div>
      </div>
    </Card>
  );
}

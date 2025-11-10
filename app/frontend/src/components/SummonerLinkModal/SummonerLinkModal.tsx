import { useState, FormEvent } from 'react';
import styles from './SummonerLinkModal.module.css';
import { Button, Input, Modal } from '@/components';
import { REGION_NAMES } from '@/constants';
import { playersActions } from '@/actions/players';
import { useSummoner } from '@/contexts';

interface SummonerLinkModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SummonerLinkModal({ isOpen, onClose }: SummonerLinkModalProps) {
  const { refreshSummoner } = useSummoner();
  const [gameName, setGameName] = useState('');
  const [tagLine, setTagLine] = useState('');
  const [region, setRegion] = useState('americas');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await playersActions.linkSummoner({
        game_name: gameName,
        tag_line: tagLine,
        region,
      });

      if (result.success) {
        setSuccess('Account linked successfully!');
        await refreshSummoner();
        setTimeout(() => {
          onClose();
          setSuccess(null);
        }, 2000);
      } else {
        setError(result.error || 'Failed to link account');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Link Your Summoner">
      <form onSubmit={handleSubmit} className={styles.modalForm}>
        <p className={styles.modalDescription}>
          Enter your Riot ID to link your League of Legends account. We'll fetch your
          summoner data including PUUID, summoner level, and profile icon.
        </p>

        <div className={styles.riotIdContainer}>
          <div className={styles.riotIdField}>
            <Input
              label="Game Name"
              type="text"
              value={gameName}
              onChange={(e) => setGameName(e.target.value)}
              placeholder="Hide on bush"
              required
              fullWidth
            />
          </div>
          <div className={styles.riotIdSeparator}>#</div>
          <div className={styles.riotIdField}>
            <Input
              label="Tag Line"
              type="text"
              value={tagLine}
              onChange={(e) => setTagLine(e.target.value)}
              placeholder="NA1"
              required
              fullWidth
            />
          </div>
        </div>

        <div className={styles.selectContainer}>
          <label className={styles.selectLabel}>Region</label>
          <select
            className={styles.select}
            value={region}
            onChange={(e) => setRegion(e.target.value)}
          >
            {Object.entries(REGION_NAMES).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {error && <div className={styles.modalError}>{error}</div>}
        {success && <div className={styles.modalSuccess}>{success}</div>}

        <Button type="submit" loading={saving} disabled={saving} fullWidth>
          {saving ? 'Linking...' : 'Link Account'}
        </Button>
      </form>
    </Modal>
  );
}
import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ProfilePage.module.css';
import { Button, Input, Card } from '@/components';
import { authActions } from '@/actions/auth';
import { playersActions } from '@/actions/players';
import { ROUTES } from '@/config';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [summoner, setSummoner] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form fields
  const [gameName, setGameName] = useState('');
  const [tagLine, setTagLine] = useState('');
  const [region, setRegion] = useState('americas');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    if (!authActions.isAuthenticated()) {
      navigate(ROUTES.LOGIN);
      return;
    }

    const userData = authActions.getCurrentUser();
    setUser(userData);

    const summonerResult = await playersActions.getSummoner();
    if (summonerResult.success && summonerResult.data) {
      setSummoner(summonerResult.data);
      // Pre-fill form if summoner exists
      if (summonerResult.data.game_name) {
        setGameName(summonerResult.data.game_name);
      }
      if (summonerResult.data.tag_line) {
        setTagLine(summonerResult.data.tag_line);
      }
      if (summonerResult.data.region) {
        setRegion(summonerResult.data.region);
      }
    }

    setLoading(false);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    const result = await playersActions.linkAccount({
      game_name: gameName,
      tag_line: tagLine,
      region,
    });

    if (result.success) {
      setSuccess('League of Legends account linked successfully!');
      setSummoner(result.data);
    } else {
      setError(result.error || 'Failed to link account');
    }

    setSaving(false);
  };

  const handleLogout = async () => {
    await authActions.logout();
    navigate(ROUTES.LOGIN);
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Profile Settings</h1>
        <div className={styles.headerButtons}>
          <Button variant="secondary" onClick={() => navigate(ROUTES.DASHBOARD)}>
            Back to Dashboard
          </Button>
          <Button variant="secondary" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </div>

      <div className={styles.content}>
        <Card title="Account Information">
          <div className={styles.info}>
            <div className={styles.infoRow}>
              <span className={styles.label}>Email:</span>
              <span className={styles.value}>{user?.email}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.label}>User ID:</span>
              <span className={styles.value}>{user?.user_id}</span>
            </div>
          </div>
        </Card>

        <Card title="Link League of Legends Account">
          <form onSubmit={handleSubmit} className={styles.form}>
            <p className={styles.description}>
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
                <option value="americas">Americas (NA, BR, LAN, LAS)</option>
                <option value="europe">Europe (EUW, EUNE, TR, RU)</option>
                <option value="asia">Asia (KR, JP)</option>
                <option value="sea">SEA (OCE, PH, SG, TH, TW, VN)</option>
              </select>
            </div>

            {error && <div className={styles.error}>{error}</div>}
            {success && <div className={styles.success}>{success}</div>}

            <Button type="submit" loading={saving} fullWidth>
              {summoner ? 'Update Account' : 'Link Account'}
            </Button>
          </form>
        </Card>

        {summoner && (
          <Card title="Linked Account">
            <div className={styles.info}>
              <div className={styles.infoRow}>
                <span className={styles.label}>Riot ID:</span>
                <span className={styles.value}>
                  {summoner.game_name}#{summoner.tag_line}
                </span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.label}>PUUID:</span>
                <span className={styles.value}>{summoner.puuid}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.label}>Summoner Level:</span>
                <span className={styles.value}>{summoner.summoner_level}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.label}>Region:</span>
                <span className={styles.value}>{summoner.region}</span>
              </div>
              {summoner.last_updated && (
                <div className={styles.infoRow}>
                  <span className={styles.label}>Last Updated:</span>
                  <span className={styles.value}>
                    {new Date(summoner.last_updated).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styles from './RegisterPage.module.css';
import { Button, Input, Card } from '@/components';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [summonerName, setSummonerName] = useState('');
  const [region, setRegion] = useState('NA1');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const result = await authActions.register({
      email,
      password,
      summoner_name: summonerName || undefined,
      region: region || undefined,
    });

    if (result.success) {
      // Check if email confirmation is required
      if (result.data?.pending_confirmation) {
        setSuccess('Account created! Please check your email to confirm your account before logging in.');
        setLoading(false);
        // Don't navigate - let user see the message
      } else {
        navigate(ROUTES.DASHBOARD);
      }
    } else {
      setError(result.error || 'Registration failed');
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Card className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.title}>Create Account</h1>
          <p className={styles.subtitle}>Join Rift Rewind</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            fullWidth
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            fullWidth
          />

          <Input
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            required
            fullWidth
          />

          <div className={styles.divider}>
            <span>Optional: Link your League account</span>
          </div>

          <Input
            label="Summoner Name (Optional)"
            type="text"
            value={summonerName}
            onChange={(e) => setSummonerName(e.target.value)}
            placeholder="Hide on bush"
            fullWidth
          />

          <div className={styles.selectContainer}>
            <label className={styles.selectLabel}>Region (Optional)</label>
            <select
              className={styles.select}
              value={region}
              onChange={(e) => setRegion(e.target.value)}
            >
              <option value="NA1">North America</option>
              <option value="EUW1">Europe West</option>
              <option value="EUN1">Europe Nordic & East</option>
              <option value="KR">Korea</option>
              <option value="BR1">Brazil</option>
              <option value="JP1">Japan</option>
              <option value="LA1">Latin America North</option>
              <option value="LA2">Latin America South</option>
              <option value="OC1">Oceania</option>
              <option value="TR1">Turkey</option>
              <option value="RU">Russia</option>
            </select>
          </div>

          {error && <div className={styles.error}>{error}</div>}
          {success && <div className={styles.success}>{success}</div>}

          <Button type="submit" loading={loading} fullWidth disabled={!!success}>
            Create Account
          </Button>
        </form>

        <div className={styles.footer}>
          <p>
            Already have an account?{' '}
            <Link to={ROUTES.LOGIN} className={styles.link}>
              Login
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}

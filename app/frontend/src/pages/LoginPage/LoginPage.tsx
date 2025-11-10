import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styles from './LoginPage.module.css';
import { Button, Input, Card, RegionBanner } from '@/components';
import { authActions } from '@/actions/auth';
import { useSummoner } from '@/contexts';
import { ROUTES } from '@/config';

export default function LoginPage() {
  const navigate = useNavigate();
  const { refreshSummoner } = useSummoner();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const result = await authActions.login({ email, password });

    if (result.success) {
      // Refresh summoner data after successful login
      await refreshSummoner();
      navigate(ROUTES.HOME);
    } else {
      setError(result.error || null);
    }

    setLoading(false);
  };

  return (
    <>
      <div className={styles.container}>
        <Card className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.title}>Welcome Back</h1>
          <p className={styles.subtitle}>Login to Heimer Academy</p>
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

          {error && <div className={styles.error}>{error}</div>}

          <Button type="submit" loading={loading} fullWidth>
            Login
          </Button>
        </form>

        <div className={styles.footer}>
          <p>
            Don't have an account?{' '}
            <Link to={ROUTES.REGISTER} className={styles.link}>
              Sign up
            </Link>
          </p>
        </div>
      </Card>
    </div>
    </>
  );
}

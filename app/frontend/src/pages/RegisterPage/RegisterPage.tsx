import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styles from './RegisterPage.module.css';
import { Button, Input, Card, RegionBanner, TermsModal } from '@/components';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showTermsModal, setShowTermsModal] = useState(false);

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
    <>
      <div className={styles.container}>
        <Card className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.title}>Create Account</h1>
          <p className={styles.subtitle}>Join Heimer Academy</p>
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

          <div className={styles.termsText}>
            By making an account, you are agreeing to our{' '}
            <button
              type="button"
              className={styles.termsLink}
              onClick={() => setShowTermsModal(true)}
            >
              Terms and Conditions
            </button>.
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
            <button
              type="button"
              className={styles.termsLink}
              onClick={() => navigate(ROUTES.LOGIN)}
            >
              Login
            </button>
          </p>
        </div>
      </Card>

      <TermsModal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
      />
    </div>
    </>
  );
}

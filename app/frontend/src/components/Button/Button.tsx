import { ButtonHTMLAttributes } from 'react';
import styles from './Button.module.css';
import Spinner from '../Spinner/Spinner';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  fullWidth?: boolean;
  loading?: boolean;
}

export default function Button({
  children,
  variant = 'primary',
  fullWidth = false,
  loading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  const classNames = [
    styles.button,
    styles[variant],
    fullWidth && styles.fullWidth,
    loading && styles.loading,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classNames} disabled={disabled || loading} {...props}>
      {loading ? (
        <span className={styles.loadingContent}>
          <Spinner size="small" />
          <span>Loading...</span>
        </span>
      ) : children}
    </button>
  );
}

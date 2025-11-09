import { useEffect, useState } from 'react';
import styles from './SyncStatusModal.module.css';
import { Spinner } from '@/components';

interface SyncStatusModalProps {
  isVisible: boolean;
  onDismiss?: () => void;
}

const SYNC_STORAGE_KEY = 'rift_rewind_sync_status';

interface SyncStatus {
  startTime: number;
  endTime: number;
}

export default function SyncStatusModal({ isVisible, onDismiss }: SyncStatusModalProps) {
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [showModal, setShowModal] = useState(false);

  // Check localStorage on mount
  useEffect(() => {
    const checkSyncStatus = () => {
      const stored = localStorage.getItem(SYNC_STORAGE_KEY);
      if (stored) {
        const syncStatus: SyncStatus = JSON.parse(stored);
        const now = Date.now();
        const elapsed = now - syncStatus.startTime;
        const duration = 5 * 60 * 1000; // 5 minutes

        if (elapsed < duration) {
          // Still syncing
          setShowModal(true);
          setIsComplete(false);
          const currentProgress = Math.min((elapsed / duration) * 100, 95);
          setProgress(currentProgress);
        } else if (elapsed < duration + 10000) {
          // Just completed (within 10 seconds of completion)
          setShowModal(true);
          setIsComplete(true);
          setProgress(100);
        } else {
          // Sync completed more than 10 seconds ago, clean up
          localStorage.removeItem(SYNC_STORAGE_KEY);
        }
      }
    };

    checkSyncStatus();
  }, []);

  // Handle new sync start
  useEffect(() => {
    if (isVisible && !showModal) {
      const startTime = Date.now();
      const endTime = startTime + (5 * 60 * 1000);
      const syncStatus: SyncStatus = { startTime, endTime };
      localStorage.setItem(SYNC_STORAGE_KEY, JSON.stringify(syncStatus));
      setShowModal(true);
      setIsComplete(false);
      setProgress(0);
    }
  }, [isVisible]);

  // Progress animation
  useEffect(() => {
    if (showModal && !isComplete) {
      const interval = setInterval(() => {
        const stored = localStorage.getItem(SYNC_STORAGE_KEY);
        if (!stored) {
          setShowModal(false);
          return;
        }

        const syncStatus: SyncStatus = JSON.parse(stored);
        const now = Date.now();
        const elapsed = now - syncStatus.startTime;
        const duration = 5 * 60 * 1000;

        if (elapsed >= duration) {
          // Sync complete!
          setProgress(100);
          setIsComplete(true);
          // Auto-dismiss after 5 seconds
          setTimeout(() => {
            localStorage.removeItem(SYNC_STORAGE_KEY);
            setShowModal(false);
            if (onDismiss) onDismiss();
          }, 5000);
        } else {
          // Update progress
          const currentProgress = Math.min((elapsed / duration) * 100, 95);
          setProgress(currentProgress);
        }
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [showModal, isComplete, onDismiss]);

  const handleDismiss = () => {
    if (isComplete) {
      localStorage.removeItem(SYNC_STORAGE_KEY);
    }
    setShowModal(false);
    if (onDismiss) onDismiss();
  };

  if (!showModal) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <div className={styles.iconWrapper}>
            {isComplete ? (
              <div className={styles.checkmark}>✓</div>
            ) : (
              <Spinner size="medium" />
            )}
          </div>
          <h3 className={styles.title}>
            {isComplete ? 'Sync Complete!' : 'Syncing in Progress'}
          </h3>
        </div>
        
        <div className={styles.content}>
          {isComplete ? (
            <>
              <p className={styles.message}>
                Your match history has been successfully synced! All data is now up to date.
              </p>
              <p className={styles.success}>
                ✓ All done! You can now view your complete match history and statistics.
              </p>
            </>
          ) : (
            <>
              <p className={styles.message}>
                We're fetching your match history from Riot Games. This may take a few moments.
              </p>
              <p className={styles.warning}>
                ⚠️ Information may not be accurate until sync is complete.
              </p>
              
              <div className={styles.progressBar}>
                <div 
                  className={styles.progressFill} 
                  style={{ width: `${progress}%` }}
                />
              </div>
              
              <p className={styles.subtext}>
                You can continue browsing while we sync your data in the background.
              </p>
            </>
          )}
        </div>

        <button className={styles.dismissButton} onClick={handleDismiss}>
          {isComplete ? 'Close' : 'Dismiss'}
        </button>
      </div>
    </div>
  );
}

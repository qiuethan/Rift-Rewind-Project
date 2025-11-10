import { useState } from 'react';
import { useAudio } from '@/contexts/AudioContext';
import styles from './AudioControls.module.css';

const soundOnIconPath = '/img/emotes/sound.png';
const soundOffIconPath = '/img/emotes/soundoff.png';

export default function AudioControls() {
  const { isPlaying, volume, toggleAudio, setVolume } = useAudio();
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    if (isPlaying) {
      // If turning off, set volume to 0
      setVolume(0);
    } else {
      // If turning on, set volume to 40%
      setVolume(0.4);
    }
    toggleAudio();
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    
    // If audio is off and user moves slider above 0, turn it on
    if (!isPlaying && newVolume > 0) {
      toggleAudio();
    }
  };

  const displayVolume = Math.round(volume * 100);
  const showSoundIcon = isPlaying && volume > 0;

  return (
    <div 
      className={`${styles.audioControls} ${isExpanded ? styles.expanded : ''}`}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      <button 
        onClick={handleToggle} 
        className={styles.toggleButton}
        aria-label="Toggle music"
      >
        <img
          src={showSoundIcon ? soundOnIconPath : soundOffIconPath}
          alt={showSoundIcon ? 'Mute audio' : 'Unmute audio'}
          className={styles.icon}
        />
      </button>

      <div className={styles.volumeContainer}>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={volume}
          onChange={handleVolumeChange}
          className={styles.volumeSlider}
          aria-label="Volume control"
        />
        <span className={styles.volumeLabel}>{displayVolume}%</span>
      </div>
    </div>
  );
}

import React, { 
  createContext, 
  useState, 
  useRef, 
  useCallback, 
  useContext, 
  ReactNode,
  useEffect
} from 'react';

interface AudioContextType {
  isPlaying: boolean;
  volume: number;
  toggleAudio: () => void;
  setVolume: (volume: number) => void;
}


const AudioContext = createContext<AudioContextType | undefined>(undefined);


export const useAudio = (): AudioContextType => {
  const context = useContext(AudioContext);
  if (context === undefined) {
    throw new Error('useAudio must be used within an AudioProvider');
  }
  return context;
};

interface AudioProviderProps {
  children: ReactNode; 
  audioSrc: string;
}

export const AudioProvider: React.FC<AudioProviderProps> = ({ children, audioSrc }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolumeState] = useState(0); // Default volume 0%
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (!audioRef.current) {
        audioRef.current = new Audio(audioSrc);
        audioRef.current.loop = true;
        audioRef.current.volume = volume;
    }
  }, [audioSrc, volume]);

  // Update audio volume when volume state changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  const toggleAudio = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play().catch(error => {
        console.error("Audio playback failed:", error);
        setIsPlaying(false); 
      });
    }
    setIsPlaying(prevIsPlaying => !prevIsPlaying);
  }, [isPlaying]);

  const setVolume = useCallback((newVolume: number) => {
    const clampedVolume = Math.max(0, Math.min(1, newVolume));
    setVolumeState(clampedVolume);
  }, []);

  const value: AudioContextType = { isPlaying, volume, toggleAudio, setVolume };

  return (
    <AudioContext.Provider value={value}>
      {children}
    </AudioContext.Provider>
  );
};
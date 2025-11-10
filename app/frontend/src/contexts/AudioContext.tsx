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
  toggleAudio: () => void;
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
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (!audioRef.current) {
        audioRef.current = new Audio(audioSrc);
        audioRef.current.loop = true;
    }
  }, [audioSrc]);

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

  const value: AudioContextType = { isPlaying, toggleAudio };

  return (
    <AudioContext.Provider value={value}>
      {children}
    </AudioContext.Provider>
  );
};
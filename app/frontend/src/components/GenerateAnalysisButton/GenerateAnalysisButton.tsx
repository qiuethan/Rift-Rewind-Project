import { useState, useEffect } from 'react';
import styles from './GenerateAnalysisButton.module.css';

// Simple inline markdown parser for bold text
const parseInlineMarkdown = (text: string): (string | JSX.Element)[] => {
  const parts = text.split('**');
  return parts.map((part, idx) => 
    idx % 2 === 1 ? <strong key={idx}>{part}</strong> : part
  );
};

interface GenerateAnalysisButtonProps {
  onGenerate: () => Promise<{ summary: string; fullAnalysis: string } | null>;
  onOpenFullAnalysis: () => void;
  cachedAnalysis?: { summary: string; fullAnalysis: string } | null;
  disabled?: boolean;
}

export default function GenerateAnalysisButton({ onGenerate, onOpenFullAnalysis, cachedAnalysis, disabled }: GenerateAnalysisButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [summary, setSummary] = useState<string | null>(cachedAnalysis?.summary || null);
  const [hasAnalysis, setHasAnalysis] = useState(!!cachedAnalysis);
  const [bubbleDismissed, setBubbleDismissed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update when cached analysis changes
  useEffect(() => {
    if (cachedAnalysis) {
      setSummary(cachedAnalysis.summary);
      setHasAnalysis(true);
      setBubbleDismissed(false); // Show bubble when new analysis is cached
      setError(null); // Clear any errors
    }
  }, [cachedAnalysis]);

  const handleClick = async () => {
    // If has analysis, just show the bubble again
    if (hasAnalysis) {
      setBubbleDismissed(false);
      return;
    }
    
    if (isGenerating || disabled) return;
    
    setIsGenerating(true);
    setBubbleDismissed(false); // Show bubble when generating
    setError(null); // Clear previous errors
    
    try {
      const result = await onGenerate();
      if (result) {
        setSummary(result.summary);
        setHasAnalysis(true);
        setError(null);
      } else {
        // Generation failed but didn't throw
        setError("Failed to generate analysis. Please try again.");
      }
    } catch (err) {
      // Handle unexpected errors
      setError("An error occurred while generating analysis. Please try again.");
      console.error('Analysis generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDismiss = (e: React.MouseEvent) => {
    e.stopPropagation();
    setBubbleDismissed(true);
  };

  return (
    <div className={styles.container}>
      {/* Thought Bubble - Visible unless dismissed */}
      {!bubbleDismissed && (
        <div className={styles.thoughtBubble}>
          <button className={styles.dismissButton} onClick={handleDismiss} title="Dismiss">
            ✕
          </button>
          <div className={styles.bubbleContent}>
            {isGenerating ? (
              <p className={styles.thinkingText}>The Professor is thinking...</p>
            ) : error ? (
              <>
                <p className={styles.errorText}>{error}</p>
                <button className={styles.retryButton} onClick={handleClick}>
                  Try Again
                </button>
              </>
            ) : hasAnalysis && summary ? (
              <>
                <p className={styles.summaryText}>{parseInlineMarkdown(summary)}</p>
                <button className={styles.readMoreButton} onClick={onOpenFullAnalysis}>
                  Show Full Analysis
                </button>
              </>
            ) : (
              <p className={styles.inviteText}>Let the Professor analyze your performance!</p>
            )}
          </div>
          <div className={styles.bubbleTail}></div>
        </div>
      )}

      {/* Heimerdinger Button - Using Emote */}
      <button
        className={`${styles.heimerButton} ${isGenerating ? styles.generating : ''} ${disabled ? styles.disabled : ''} ${hasAnalysis ? styles.hasAnalysis : ''}`}
        onClick={handleClick}
        disabled={isGenerating || disabled}
        title={hasAnalysis ? "Click to show analysis" : "Generate Analysis"}
      >
        <img 
          src="/img/emotes/heimerdinger.png"
          alt="Heimerdinger"
          className={styles.heimerImage}
        />
      </button>
    </div>
  );
}

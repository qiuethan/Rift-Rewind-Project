import { useState, useEffect } from 'react';
import styles from './HeimerdingerModal.module.css';

// Simple markdown parser for analysis text
const parseMarkdown = (text: string): JSX.Element[] => {
  const lines = text.split('\n');
  const elements: JSX.Element[] = [];
  let key = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Headers
    if (line.startsWith('### ')) {
      elements.push(<h3 key={key++} className={styles.mdH3}>{line.substring(4)}</h3>);
    } else if (line.startsWith('## ')) {
      elements.push(<h2 key={key++} className={styles.mdH2}>{line.substring(3)}</h2>);
    } else if (line.startsWith('# ')) {
      elements.push(<h1 key={key++} className={styles.mdH1}>{line.substring(2)}</h1>);
    }
    // Bold text
    else if (line.includes('**')) {
      const parts = line.split('**');
      const formatted = parts.map((part, idx) => 
        idx % 2 === 1 ? <strong key={`${key}-${idx}`}>{part}</strong> : part
      );
      elements.push(<p key={key++} className={styles.mdP}>{formatted}</p>);
    }
    // Bullet points
    else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const content = line.trim().substring(2);
      // Check if bold
      if (content.includes('**')) {
        const parts = content.split('**');
        const formatted = parts.map((part, idx) => 
          idx % 2 === 1 ? <strong key={`${key}-${idx}`}>{part}</strong> : part
        );
        elements.push(<li key={key++} className={styles.mdLi}>{formatted}</li>);
      } else {
        elements.push(<li key={key++} className={styles.mdLi}>{content}</li>);
      }
    }
    // Empty line
    else if (line.trim() === '') {
      elements.push(<br key={key++} />);
    }
    // Regular paragraph
    else if (line.trim()) {
      // Check if bold
      if (line.includes('**')) {
        const parts = line.split('**');
        const formatted = parts.map((part, idx) => 
          idx % 2 === 1 ? <strong key={`${key}-${idx}`}>{part}</strong> : part
        );
        elements.push(<p key={key++} className={styles.mdP}>{formatted}</p>);
      } else {
        elements.push(<p key={key++} className={styles.mdP}>{line}</p>);
      }
    }
  }

  return elements;
};

interface HeimerdingerModalProps {
  isOpen: boolean;
  onClose: () => void;
  summary: string;
  fullAnalysis: string;
  title: string;
}

export default function HeimerdingerModal({ isOpen, onClose, summary, fullAnalysis, title }: HeimerdingerModalProps) {
  const [activeView, setActiveView] = useState<'summary' | 'full'>('full');

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button className={styles.closeButton} onClick={onClose} title="Close">
          ✕
        </button>

        {/* Decorative Gears */}
        <div className={styles.gearTopLeft}>⚙</div>
        <div className={styles.gearTopRight}>⚙</div>
        <div className={styles.gearBottomLeft}>⚙</div>
        <div className={styles.gearBottomRight}>⚙</div>

        {/* Header with Heimerdinger */}
        <div className={styles.header}>
          <img 
            src="/img/emotes/heimerdinger.png"
            alt="Heimerdinger"
            className={styles.heimerLogo}
          />
          <div className={styles.headerText}>
            <h2 className={styles.title}>Professor Heimerdinger's Analysis</h2>
            <p className={styles.subtitle}>{title}</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeView === 'summary' ? styles.activeTab : ''}`}
            onClick={() => setActiveView('summary')}
          >
            Quick Summary
          </button>
          <button
            className={`${styles.tab} ${activeView === 'full' ? styles.activeTab : ''}`}
            onClick={() => setActiveView('full')}
          >
            Detailed Analysis
          </button>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {activeView === 'summary' ? (
            <div className={styles.summary}>
              <div className={styles.summaryBox}>
                <div className={styles.summaryText}>{parseMarkdown(summary)}</div>
              </div>
            </div>
          ) : (
            <div className={styles.fullAnalysis}>
              <div className={styles.analysisBox}>
                <div className={styles.analysisText}>{parseMarkdown(fullAnalysis)}</div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <div className={styles.professorQuote}>
            "Science is the key to progress!" - Heimerdinger
          </div>
          <button className={styles.confirmButton} onClick={onClose}>
            ✓ Got it, Professor!
          </button>
        </div>
      </div>
    </div>
  );
}

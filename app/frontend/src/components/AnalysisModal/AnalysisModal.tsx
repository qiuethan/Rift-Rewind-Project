import { useState } from 'react';
import styles from './AnalysisModal.module.css';
import { Modal } from '@/components';

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

interface AnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  summary: string;
  fullAnalysis: string;
  title: string;
}

export default function AnalysisModal({ isOpen, onClose, summary, fullAnalysis, title }: AnalysisModalProps) {
  const [activeView, setActiveView] = useState<'summary' | 'full'>('full');

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="">
      <div className={styles.heimerModal}>
        {/* Heimerdinger Header */}
        <div className={styles.header}>
          <img 
            src="https://ddragon.leagueoflegends.com/cdn/15.22.1/img/champion/Heimerdinger.png"
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
            ⚡ Quick Summary
          </button>
          <button
            className={`${styles.tab} ${activeView === 'full' ? styles.activeTab : ''}`}
            onClick={() => setActiveView('full')}
          >
            🔬 Detailed Analysis
          </button>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {activeView === 'summary' ? (
            <div className={styles.summary}>
              <div className={styles.summaryBox}>
                <div className={styles.summaryIcon}>💡</div>
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
          <button className={styles.closeButton} onClick={onClose}>
            ✓ Got it, Professor!
          </button>
        </div>
      </div>
    </Modal>
  );
}

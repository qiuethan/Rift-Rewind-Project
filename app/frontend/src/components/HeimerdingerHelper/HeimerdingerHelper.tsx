import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import styles from './HeimerdingerHelper.module.css';
import { HeimerdingerModal } from '@/components';

// Simple inline markdown parser for bold text
const parseInlineMarkdown = (text: string): (string | JSX.Element)[] => {
  const parts = text.split('**');
  return parts.map((part, idx) => 
    idx % 2 === 1 ? <strong key={idx}>{part}</strong> : part
  );
};

// Route-specific instructions
const getInstructions = (pathname: string) => {
  if (pathname === '/' || pathname === '/home') {
    return {
      summary: "Welcome to **Heimer Academy**! Your personal League of Legends performance analyzer.",
      details: `# Welcome to Heimer Academy!

## What is Heimer Academy?

Heimer Academy is your comprehensive League of Legends performance analysis tool. Track your progress, analyze your matches, and improve your gameplay with AI-powered insights.

## Getting Started

**Link Your Account**: Connect your Riot Games account to start tracking your matches.

**View Dashboard**: See your overall performance statistics and recent games.

**Analyze Matches**: Deep dive into your match history with AI-powered performance insights and actionable recommendations.

**Discover Champions**: Find champions that match your playstyle and maximize your win rate based on your unique strengths.

## Features

**Match Analysis**: Deep dive into your match history with AI-powered performance insights and actionable recommendations.

**New Champions**: Discover champions that match your playstyle and maximize your win rate based on your unique strengths.

**Skill Progression**: Track your improvement over time with detailed analytics and personalized training recommendations.

**AI Insights**: Get intelligent feedback on your gameplay patterns, decision-making, and strategic opportunities.

Start by linking your account to unlock all features!`
    };
  }

  if (pathname === '/dashboard') {
    return {
      summary: "Your **Dashboard** shows overall performance, recent matches, and quick stats at a glance.",
      details: `# Dashboard Overview

## What You'll See

**Performance Summary**: Your overall win rate, KDA, and recent performance trends.

**Recent Matches**: Quick view of your last few games with key statistics.

**Champion Mastery**: Your most played champions and mastery levels.

**Quick Stats**: Important metrics like average CS, damage, and vision score.

## Navigation

Click on any match to see detailed analysis.

Visit the Champions page to see champion-specific progress.

Check the Games page for your full match history.`
    };
  }

  if (pathname === '/games') {
    return {
      summary: "Browse your **Match History** with detailed stats for each game.",
      details: `# Games Page

## Match History

View all your tracked matches with key performance indicators.

## Features

**Filter Matches**: Sort by date, champion, or outcome.

**Quick Stats**: See KDA, CS, damage, and more at a glance.

**Detailed Analysis**: Click any match to see in-depth performance metrics.

## Tips

Recent matches appear at the top.

Use filters to find specific games or champions.

Click on a match card to open the detailed analysis page.`
    };
  }

  if (pathname === '/champions') {
    return {
      summary: "View your **Champion Pool** and track mastery progression for each champion.",
      details: `# Champions Page

## Champion Mastery

See all champions you've played with mastery levels and statistics.

## Features

**Mastery Levels**: Track your progress toward mastery 7.

**Performance Stats**: Win rate, KDA, and games played per champion.

**Champion Details**: Click any champion to see detailed progression.

## Tips

Champions are sorted by mastery points.

Click a champion card to see match history and trends.

Track your improvement over time with each champion.`
    };
  }

  if (pathname === '/recommend') {
    return {
      summary: "Get **Champion Recommendations** based on your playstyle and performance.",
      details: `# Recommendations

## Personalized Suggestions

Discover champions that match your playstyle and strengths.

## How It Works

**Analysis**: We analyze your performance across all champions.

**Matching**: Find champions that suit your strengths.

**Suggestions**: Get personalized recommendations to expand your pool.

## Tips

Try recommended champions in normal games first.

Focus on champions that match your preferred role.

Experiment with different playstyles to find what works best.`
    };
  }

  // Default instructions
  return {
    summary: "Need help? Click **Learn More** for detailed instructions about this page.",
    details: `# Page Instructions

This page is part of Heimer Academy, your League of Legends performance tracker.

## Navigation

Use the navigation bar to explore different sections.

## Features

Each page offers unique insights into your gameplay with AI-powered analysis.

Click on items to see more detailed information.

## Support

If you need help, check the instructions on each page. Professor Heimerdinger is here to guide you!`
  };
};

interface HeimerdingerHelperProps {
  disabled?: boolean;
}

export default function HeimerdingerHelper({ disabled }: HeimerdingerHelperProps) {
  const location = useLocation();
  const [bubbleDismissed, setBubbleDismissed] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const instructions = getInstructions(location.pathname);

  const handleClick = () => {
    if (disabled) return;
    setBubbleDismissed(false); // Show bubble when clicked
  };

  const handleDismiss = (e: React.MouseEvent) => {
    e.stopPropagation();
    setBubbleDismissed(true);
  };

  const handleOpenDetails = () => {
    setShowModal(true);
  };

  return (
    <>
      <div className={styles.container}>
        {/* Thought Bubble - Visible unless dismissed */}
        {!bubbleDismissed && (
          <div className={styles.thoughtBubble}>
            <button className={styles.dismissButton} onClick={handleDismiss} title="Dismiss">
              ✕
            </button>
            <div className={styles.bubbleContent}>
              <p className={styles.summaryText}>{parseInlineMarkdown(instructions.summary)}</p>
              <button className={styles.readMoreButton} onClick={handleOpenDetails}>
                Learn More
              </button>
            </div>
            <div className={styles.bubbleTail}></div>
          </div>
        )}

        {/* Heimerdinger Button - Using Emote */}
        <button
          className={`${styles.heimerButton} ${disabled ? styles.disabled : ''}`}
          onClick={handleClick}
          disabled={disabled}
          title="Show page instructions"
        >
          <img 
            src="/img/emotes/heimerdinger.png"
            alt="Heimerdinger"
            className={styles.heimerImage}
          />
        </button>
      </div>

      {/* Instructions Modal */}
      <HeimerdingerModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        summary={instructions.summary}
        fullAnalysis={instructions.details}
        title="Page Instructions"
      />
    </>
  );
}

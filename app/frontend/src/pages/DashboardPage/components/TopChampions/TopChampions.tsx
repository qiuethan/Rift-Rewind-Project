import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Spinner, Input } from '@/components';
import { getChampionKey, getChampionIconUrl, FALLBACK_ICON_URL } from '@/constants';
import styles from './TopChampions.module.css';

interface TopChampionsProps {
  champions?: any[];
  loading?: boolean;
}

export default function TopChampions({ champions, loading }: TopChampionsProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [hasDragged, setHasDragged] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  if (loading) {
    return (
      <Card>
        <div className={styles.loading}>
          <Spinner />
          <p>Loading champion mastery...</p>
        </div>
      </Card>
    );
  }

  if (!champions || champions.length === 0) {
    return null;
  }

  // Filter champions based on search query
  const filteredChampions = champions.filter((champ: any) => {
    const championId = champ.championId || champ.champion_id;
    const championKey = getChampionKey(championId);
    return championKey.toLowerCase().includes(searchQuery.toLowerCase());
  });

  // Drag handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setHasDragged(false);
    setStartX(e.pageX - (scrollRef.current?.offsetLeft || 0));
    setScrollLeft(scrollRef.current?.scrollLeft || 0);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    e.preventDefault();
    setHasDragged(true);
    const x = e.pageX - (scrollRef.current?.offsetLeft || 0);
    const walk = (x - startX) * 1.5; // Scroll speed multiplier
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollLeft - walk;
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
  };

  return (
    <Card>
      <div className={styles.header}>
        <h3 className={styles.title}>Your Champions</h3>
        <div className={styles.searchContainer}>
          <Input
            type="text"
            placeholder="Search champions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>
      </div>
      {filteredChampions.length === 0 ? (
        <div className={styles.noResults}>
          <p>No champions found matching "{searchQuery}"</p>
        </div>
      ) : (
        <div 
          className={`${styles.championsScroll} ${isDragging ? styles.dragging : ''}`}
          ref={scrollRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseLeave}
        >
          {filteredChampions.map((champ: any) => {
            // Handle both camelCase (from API) and snake_case (from DB)
            const championId = champ.championId || champ.champion_id;
            const championLevel = champ.championLevel || champ.champion_level;
            const championPoints = champ.championPoints || champ.champion_points;
            const championKey = getChampionKey(championId);

            return (
              <div 
                key={championId} 
                className={styles.championCard}
                onClick={() => !hasDragged && navigate(`/champion/${championKey.toLowerCase()}`, { state: { from: 'dashboard' } })}
              >
                <img
                  src={getChampionIconUrl(championKey)}
                  alt={championKey}
                  className={styles.championIcon}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = FALLBACK_ICON_URL;
                  }}
                />
                <div className={styles.championInfo}>
                  <div className={styles.championName}>{championKey}</div>
                  <div className={styles.championLevel}>Level {championLevel}</div>
                  <div className={styles.championPoints}>
                    {(championPoints / 1000).toFixed(0)}k points
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}

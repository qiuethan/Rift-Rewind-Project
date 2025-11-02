import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Navbar.module.css';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';
import RegionSelector from '../RegionSelector';

interface NavbarProps {
  user?: any;
  summoner?: any;
}

export default function Navbar({ user, summoner }: NavbarProps) {
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await authActions.logout();
    navigate(ROUTES.LOGIN);
  };

  const profileIconUrl = summoner?.profile_icon_id
    ? `https://ddragon.leagueoflegends.com/cdn/15.21.1/img/profileicon/${summoner.profile_icon_id}.png`
    : 'https://ddragon.leagueoflegends.com/cdn/15.21.1/img/profileicon/29.png'; // Default icon

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <div className={styles.logo} onClick={() => navigate(ROUTES.DASHBOARD)}>
          <span className={styles.logoText}>Rift Rewind</span>
        </div>

        <div className={styles.nav}>
          <button 
            className={styles.navLink} 
            onClick={() => navigate(ROUTES.DASHBOARD)}
          >
            Dashboard
          </button>
          <button 
            className={styles.navLink} 
            onClick={() => navigate(ROUTES.GAMES)}
          >
            Games
          </button>
          <button 
            className={styles.navLink} 
            onClick={() => navigate(ROUTES.ANALYTICS)}
          >
            Analytics
          </button>
          <button 
            className={styles.navLink} 
            onClick={() => navigate(ROUTES.CHAMPIONS)}
          >
            Champions
          </button>
        </div>

        <div className={styles.rightSection}>
          <RegionSelector />
          
          <div className={styles.profile} ref={dropdownRef}>
          <button 
            className={styles.profileButton}
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            <img 
              src={profileIconUrl}
              alt="Profile"
              className={styles.profileIcon}
            />
            <span className={styles.profileName}>
              {summoner?.game_name || user?.email?.split('@')[0] || 'User'}
            </span>
          </button>

          {isDropdownOpen && (
            <div className={styles.dropdown}>
              <div className={styles.dropdownHeader}>
                <img 
                  src={profileIconUrl}
                  alt="Profile"
                  className={styles.dropdownIcon}
                />
                <div className={styles.dropdownInfo}>
                  <div className={styles.dropdownName}>
                    {summoner?.summoner_name || user?.email}
                  </div>
                  {summoner && (
                    <div className={styles.dropdownLevel}>
                      Level {summoner.summoner_level}
                    </div>
                  )}
                </div>
              </div>

              <div className={styles.dropdownDivider} />

              <button 
                className={styles.dropdownItem}
                onClick={() => {
                  navigate(ROUTES.DASHBOARD);
                  setIsDropdownOpen(false);
                }}
              >
                Dashboard
              </button>
              <button 
                className={styles.dropdownItem}
                onClick={() => {
                  navigate(ROUTES.GAMES);
                  setIsDropdownOpen(false);
                }}
              >
                Games
              </button>
              <button 
                className={styles.dropdownItem}
                onClick={() => {
                  navigate(ROUTES.ANALYTICS);
                  setIsDropdownOpen(false);
                }}
              >
                Analytics
              </button>
              <button 
                className={styles.dropdownItem}
                onClick={() => {
                  navigate(ROUTES.CHAMPIONS);
                  setIsDropdownOpen(false);
                }}
              >
                Champions
              </button>

              <div className={styles.dropdownDivider} />

              <button 
                className={styles.dropdownItem}
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          )}
        </div>
        </div>
      </div>
    </nav>
  );
}

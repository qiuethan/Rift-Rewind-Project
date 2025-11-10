import { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styles from './Navbar.module.css';
import { authActions } from '@/actions/auth';
import { ROUTES } from '@/config';
import RegionSelector from '../RegionSelector';

interface NavbarProps {
  user?: any;
  summoner?: any;
  showAuthButtons?: boolean;
}

export default function Navbar({ user, summoner, showAuthButtons = false }: NavbarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  const profileIconUrl = summoner && summoner.profile_icon_id
    ? `https://ddragon.leagueoflegends.com/cdn/15.22.1/img/profileicon/${summoner.profile_icon_id}.png`
    : 'https://ddragon.leagueoflegends.com/cdn/15.22.1/img/profileicon/29.png';

  // Hide region picker on /champion/:champion routes
  const hideRegionSelector = /^\/champion\/[^/]+$/.test(location.pathname);

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <div className={styles.logo} onClick={() => navigate(ROUTES.HOME)}>
          <span className={styles.logoText}>Heimer Academy</span>
        </div>

        {!showAuthButtons && (
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
              onClick={() => navigate(ROUTES.CHAMPIONS)}
            >
              Champions
            </button>
            <button 
              className={styles.navLink} 
              onClick={() => navigate(ROUTES.RECOMMEND)}
            >
              Recommend
            </button>
          </div>
        )}

        {!hideRegionSelector && (
          <div className={styles.regionSelector}>
            <RegionSelector />
          </div>
        )}

        <div className={styles.rightSection}>
          {showAuthButtons ? (
            <div className={styles.authButtons}>
              <button className={styles.loginButton} onClick={() => navigate(ROUTES.LOGIN)}>Login</button>
              <button className={styles.registerButton} onClick={() => navigate(ROUTES.REGISTER)}>Get Started</button>
            </div>
          ) : (
            <div className={styles.profile} ref={dropdownRef}>
              <button className={styles.profileButton} onClick={() => setIsDropdownOpen(!isDropdownOpen)}>
                <img src={profileIconUrl} alt="Profile" className={styles.profileIcon} />
                <span className={styles.profileName}>
                  {summoner?.game_name || user?.email?.split('@')[0] || 'User'}
                </span>
              </button>

              {isDropdownOpen && (
                <div className={styles.dropdown}>
                  <div className={styles.dropdownHeader}>
                    <img src={profileIconUrl} alt="Profile" className={styles.dropdownIcon} />
                    <div className={styles.dropdownInfo}>
                      <div className={styles.dropdownName}>{summoner?.summoner_name || user?.email}</div>
                      {summoner && <div className={styles.dropdownLevel}>Level {summoner.summoner_level}</div>}
                    </div>
                  </div>
                  <div className={styles.dropdownDivider} />
                  <button className={styles.dropdownItem} onClick={handleLogout}>Logout</button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
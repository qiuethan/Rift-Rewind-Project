/**
 * Riot API and Data Dragon constants
 */

export const DATA_DRAGON_VERSION = '15.22.1';

export const DATA_DRAGON_BASE_URL = 'https://ddragon.leagueoflegends.com/cdn';

/**
 * Get profile icon URL
 * @param iconId - Profile icon ID
 * @param version - Data Dragon version
 * @returns URL to profile icon
 */
export const getProfileIconUrl = (iconId: number, version: string = DATA_DRAGON_VERSION): string => {
  return `${DATA_DRAGON_BASE_URL}/${version}/img/profileicon/${iconId}.png`;
};

/**
 * Fallback profile icon URL
 */
export const FALLBACK_ICON_URL = getProfileIconUrl(29);

/**
 * Region display names
 */
export const REGION_NAMES: { [key: string]: string } = {
  americas: 'Americas (NA, BR, LAN, LAS)',
  europe: 'Europe (EUW, EUNE, TR, RU)',
  asia: 'Asia (KR, JP)',
  sea: 'SEA (OCE, PH, SG, TH, TW, VN)',
};

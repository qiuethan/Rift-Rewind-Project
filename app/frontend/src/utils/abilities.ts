import championAbilitiesIndex from '@/data/champion_abilities_index.json';

interface AbilityAsset {
  name: string;
  imageUrl: string;
}

interface ChampionAbilities {
  Q: {
    name: string;
    image: string;
  };
  W: {
    name: string;
    image: string;
  };
  E: {
    name: string;
    image: string;
  };
  R: {
    name: string;
    image: string;
  };
}

interface AbilitiesIndex {
  version: string;
  champions: Record<string, ChampionAbilities>;
}

/**
 * Get ability asset information (name and image URL) for a champion's ability
 * @param championId - The champion ID (case-insensitive)
 * @param slot - The ability slot (Q, W, E, R)
 * @returns Object with name and imageUrl, or null if not found
 */
export function getAbilityAsset(
  championId: string,
  slot: 'Q' | 'W' | 'E' | 'R'
): AbilityAsset | null {
  const index = championAbilitiesIndex as AbilitiesIndex;
  const championKey = championId.toLowerCase();

  const champion = index.champions[championKey];
  if (!champion) {
    console.warn(`Champion "${championId}" not found in abilities index`);
    return null;
  }

  const ability = champion[slot];
  if (!ability) {
    console.warn(`Ability slot "${slot}" not found for champion "${championId}"`);
    return null;
  }

  return {
    name: ability.name,
    imageUrl: `https://ddragon.leagueoflegends.com/cdn/${index.version}/img/spell/${ability.image}`,
  };
}

/**
 * Get all ability assets for a champion
 * @param championId - The champion ID (case-insensitive)
 * @returns Object with Q, W, E, R ability assets, or null if champion not found
 */
export function getChampionAbilityAssets(championId: string): ChampionAbilities | null {
  const index = championAbilitiesIndex as AbilitiesIndex;
  const championKey = championId.toLowerCase();

  const champion = index.champions[championKey];
  if (!champion) {
    console.warn(`Champion "${championId}" not found in abilities index`);
    return null;
  }

  return champion;
}
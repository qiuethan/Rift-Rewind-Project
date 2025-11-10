"""
Champion name to ID mapping utility
"""
from typing import Optional, Dict, List
import json
import glob
from pathlib import Path

# Cache for champion data
_CHAMPION_DATA_CACHE: Dict[str, Dict] = {}

# Champion name to ID mapping (partial list - expand as needed)
CHAMPION_NAME_TO_ID = {
    # A
    "aatrox": 266,
    "ahri": 103,
    "akali": 84,
    "akshan": 166,
    "alistar": 12,
    "amumu": 32,
    "anivia": 34,
    "annie": 1,
    "aphelios": 523,
    "ashe": 22,
    "aurelion sol": 136,
    "azir": 268,
    
    # B
    "bard": 432,
    "bel'veth": 200,
    "blitzcrank": 53,
    "brand": 63,
    "braum": 201,
    "briar": 233,
    
    # C
    "caitlyn": 51,
    "camille": 164,
    "cassiopeia": 69,
    "cho'gath": 31,
    "corki": 42,
    
    # D
    "darius": 122,
    "diana": 131,
    "dr. mundo": 36,
    "draven": 119,
    
    # E
    "ekko": 245,
    "elise": 60,
    "evelynn": 28,
    "ezreal": 81,
    
    # F
    "fiddlesticks": 9,
    "fiora": 114,
    "fizz": 105,
    
    # G
    "galio": 3,
    "gangplank": 41,
    "garen": 86,
    "gnar": 150,
    "gragas": 79,
    "graves": 104,
    "gwen": 887,
    
    # H
    "hecarim": 120,
    "heimerdinger": 74,
    "hwei": 910,
    
    # I
    "illaoi": 420,
    "irelia": 39,
    "ivern": 427,
    
    # J
    "janna": 40,
    "jarvan iv": 59,
    "jax": 24,
    "jayce": 126,
    "jhin": 202,
    "jinx": 222,
    
    # K
    "k'sante": 897,
    "kai'sa": 145,
    "kalista": 429,
    "karma": 43,
    "karthus": 30,
    "kassadin": 38,
    "katarina": 55,
    "kayle": 10,
    "kayn": 141,
    "kennen": 85,
    "kha'zix": 121,
    "kindred": 203,
    "kled": 240,
    "kog'maw": 96,
    
    # L
    "leblanc": 7,
    "lee sin": 64,
    "leona": 89,
    "lillia": 876,
    "lissandra": 127,
    "lucian": 236,
    "lulu": 117,
    "lux": 99,
    
    # M
    "malphite": 54,
    "malzahar": 90,
    "maokai": 57,
    "master yi": 11,
    "milio": 902,
    "miss fortune": 21,
    "mordekaiser": 82,
    "morgana": 25,
    
    # N
    "naafiri": 950,
    "nami": 267,
    "nasus": 75,
    "nautilus": 111,
    "neeko": 518,
    "nidalee": 76,
    "nilah": 895,
    "nocturne": 56,
    "nunu & willump": 20,
    
    # O
    "olaf": 2,
    "orianna": 61,
    "ornn": 516,
    
    # P
    "pantheon": 80,
    "poppy": 78,
    "pyke": 555,
    
    # Q
    "qiyana": 246,
    "quinn": 133,
    
    # R
    "rakan": 497,
    "rammus": 33,
    "rek'sai": 421,
    "rell": 526,
    "renata glasc": 888,
    "renekton": 58,
    "rengar": 107,
    "riven": 92,
    "rumble": 68,
    "ryze": 13,
    
    # S
    "samira": 360,
    "sejuani": 113,
    "senna": 235,
    "seraphine": 147,
    "sett": 875,
    "shaco": 35,
    "shen": 98,
    "shyvana": 102,
    "singed": 27,
    "sion": 14,
    "sivir": 15,
    "skarner": 72,
    "smolder": 901,
    "sona": 37,
    "soraka": 16,
    "swain": 50,
    "sylas": 517,
    "syndra": 134,
    
    # T
    "tahm kench": 223,
    "taliyah": 163,
    "talon": 91,
    "taric": 44,
    "teemo": 17,
    "thresh": 412,
    "tristana": 18,
    "trundle": 48,
    "tryndamere": 23,
    "twisted fate": 4,
    "twitch": 29,
    
    # U
    "udyr": 77,
    "urgot": 6,
    
    # V
    "varus": 110,
    "vayne": 67,
    "veigar": 45,
    "vel'koz": 161,
    "vex": 711,
    "vi": 254,
    "viego": 234,
    "viktor": 112,
    "vladimir": 8,
    "volibear": 106,
    
    # W
    "warwick": 19,
    "wukong": 62,
    
    # X
    "xayah": 498,
    "xerath": 101,
    "xin zhao": 5,
    
    # Y
    "yasuo": 157,
    "yone": 777,
    "yorick": 83,
    "yuumi": 350,
    
    # Z
    "zac": 154,
    "zed": 238,
    "zeri": 221,
    "ziggs": 115,
    "zilean": 26,
    "zoe": 142,
    "zyra": 143,
}


def get_champion_id(champion_name: str) -> Optional[int]:
    """
    Get champion ID from champion name (case-insensitive)
    
    Args:
        champion_name: Champion name
        
    Returns:
        Champion ID or None if not found
    """
    return CHAMPION_NAME_TO_ID.get(champion_name.lower())


def extract_champion_from_text(text: str) -> Optional[str]:
    """
    Extract champion name from user text
    
    Args:
        text: User's message
        
    Returns:
        Champion name if found, None otherwise
    """
    text_lower = text.lower()
    
    # Check for each champion name in the text
    for champion_name in CHAMPION_NAME_TO_ID.keys():
        if champion_name in text_lower:
            return champion_name
    
    return None


# Cache for ID to graph name mapping
_ID_TO_GRAPH_NAME_CACHE: Optional[Dict[int, str]] = None


def load_id_to_graph_name_mapping() -> Dict[int, str]:
    """
    Load champion ID to graph name mapping from champion_data folder
    
    This matches the approach used in scripts/champion_recommender/utils.py
    Uses individual champion JSON files which contain the correct graph names.
    
    Returns:
        Dict mapping champion ID (int) to graph name (str)
        Example: {62: "MonkeyKing", 103: "Ahri", ...}
    """
    global _ID_TO_GRAPH_NAME_CACHE
    
    if _ID_TO_GRAPH_NAME_CACHE is not None:
        return _ID_TO_GRAPH_NAME_CACHE
    
    try:
        # Path to champion_data folder (individual champion JSONs)
        champion_data_dir = Path(__file__).resolve().parents[3] / 'data' / 'champion_data'
        
        id_to_name = {}
        
        # Load each champion JSON file
        for json_path in glob.glob(str(champion_data_dir / "*.json")):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Each file has one champion in data
                champion_data = list(data.get('data', {}).values())[0]
                champion_id = int(champion_data['key'])
                graph_name = champion_data['id']  # Graph name (e.g., "MonkeyKing")
                
                id_to_name[champion_id] = graph_name
        
        _ID_TO_GRAPH_NAME_CACHE = id_to_name
        print(f"Loaded {len(id_to_name)} champion ID mappings from champion_data folder")
        return id_to_name
        
    except Exception as e:
        print(f"Error loading champion ID to name mapping: {e}")
        return {}


def get_champion_tags(champion_name: str) -> List[str]:
    """
    Get champion tags (roles) from champion data JSON files
    
    Args:
        champion_name: Champion name (e.g., "Kayn", "Jinx")
        
    Returns:
        List of tags (e.g., ["Fighter", "Assassin"]) or empty list if not found
    """
    try:
        # Normalize champion name
        normalized_name = champion_name.replace("'", "").replace(" ", "").lower()
        
        # Check cache first
        if normalized_name in _CHAMPION_DATA_CACHE:
            return _CHAMPION_DATA_CACHE[normalized_name].get('tags', [])
        
        # Find champion data file
        champion_data_dir = Path(__file__).resolve().parents[1] / 'constants' / 'data' / 'champion_data'
        
        # Try to find the JSON file (case-insensitive)
        for json_file in champion_data_dir.glob('*.json'):
            file_name = json_file.stem.lower()
            if file_name == normalized_name or file_name == champion_name.lower():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Get the first (and only) champion data
                    champion_data = list(data.get('data', {}).values())[0]
                    tags = champion_data.get('tags', [])
                    
                    # Cache it
                    _CHAMPION_DATA_CACHE[normalized_name] = {'tags': tags}
                    return tags
        
        return []
        
    except Exception as e:
        print(f"Error loading champion tags for {champion_name}: {e}")
        return []


def get_graph_name_from_id(champion_id: int) -> Optional[str]:
    """
    Get graph champion name from champion ID
    
    Args:
        champion_id: Riot API champion ID (e.g., 62 for Wukong)
        
    Returns:
        Graph champion name (e.g., "MonkeyKing") or None if not found
    """
    mapping = load_id_to_graph_name_mapping()
    return mapping.get(champion_id)

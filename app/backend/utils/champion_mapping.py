"""
Champion name to ID mapping utility
"""
from typing import Optional

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

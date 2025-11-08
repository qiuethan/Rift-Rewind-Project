import json
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import requests
import time


from dotenv import load_dotenv
load_dotenv()

RIOT_API_KEY = os.environ["RIOT_API_KEY"]
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Region routing for match data (e.g., 'americas', 'europe', 'asia')
MATCH_REGION = os.environ["MATCH_REGION"]
REGION_KEY = os.environ["REGION_KEY"]


def riot_get(url, headers, max_retries=5):
    for i in range(max_retries):
        r = requests.get(url, headers=headers)
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 2))
            print(f"Rate limit hit. Sleeping for {retry_after}s...")
            time.sleep(retry_after + 1)
            continue
        elif r.status_code == 200:
            return r
        else:
            r.raise_for_status()
    raise RuntimeError(f"Failed after {max_retries} retries: {url}")


def get_puuid(game_name: str, tag_line: str) -> str:
    """Get player's PUUID from summoner name."""
    url = f"https://{MATCH_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["puuid"]


def get_match_ids(puuid: str, count: int = 100):
    """Get recent match IDs for a player."""
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
    resp = riot_get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_match(match_id, MATCH_REGION, HEADERS, tier=None, div=None, cache=False) -> pd.DataFrame:
    cache_dir = f"match_data/{tier}"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{match_id}.csv")

    if os.path.exists(cache_file):
        return pd.read_csv(cache_file)

    resp = riot_get(
        f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}",
        HEADERS
    )
    match_data = resp.json()
    df = pd.DataFrame([
        {"matchID": match_id, "tier": tier, "division": div, "puuid": p["puuid"], "championName": p["championName"]}
        for p in match_data["info"]["participants"]
    ])

    df["championName"] = df["championName"].str.replace(r"^Strawberry_?", "", regex=True)
    df["championName"] = df["championName"].replace("FiddleSticks", "Fiddlesticks")

    if cache:
        if os.path.exists(cache_file):
            df.to_csv(cache_file, mode="a", header=False, index=False)
        else:
            df.to_csv(cache_file, index=False)

    return df


def get_puuids_by_rank(tier, rank):
  resp = riot_get(
        f"https://{REGION_KEY}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier.upper()}/{rank.upper()}",
        HEADERS
    )
  return resp.json()


def get_puuids_master_plus(rank):
    resp = riot_get(
        f"https://{REGION_KEY}.api.riotgames.com/lol/league/v4/{rank.lower()}leagues/by-queue/RANKED_SOLO_5x5",
        HEADERS
    )
    return resp.json()



def load_champion_mappings(folder = "data/champion_data"):
    """Load champion name to ID mappings from JSON files in the specified folder.
    
    DO NOT USE THIS
    """

    champ_to_id = {}

    for path in glob.glob(os.path.join(folder, "*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            champ_data = list(data["data"].values())[0]
            champ_name = champ_data["id"]
            champ_key = int(champ_data["key"])
            
            champ_to_id[champ_name] = champ_key

    id_to_champ = {v: k for k, v in champ_to_id.items()}

    print(f"Loaded {len(champ_to_id)} champions.")
    return champ_to_id, id_to_champ


def visualize_graph(G, labels):
    plt.figure(figsize=(7,7))
    plt.xticks([])
    plt.yticks([])
    nx.draw_networkx(G, pos=nx.spring_layout(G, seed=42), with_labels=True, labels=labels,
                     node_color="lightblue", edge_color="lightgrey", cmap="Set2")
    plt.show()


def champion_node_rep(champion_dir = "data/champion_data"):
    champion_data = []

    for filename in os.listdir(champion_dir):
        if not filename.endswith(".json"):
            continue
        
        with open(os.path.join(champion_dir, filename), encoding="utf-8") as f:
            data = json.load(f)
            champ = list(data["data"].values())[0]  # root champion object
            
            name = champ["id"]
            info = champ.get("info", {})
            tags = champ.get("tags", [])
            
            champion_data.append({
                "championName": name,
                # "key": int(champ["key"]),
                "attack": info.get("attack", 0),
                "defense": info.get("defense", 0),
                "magic": info.get("magic", 0),
                "difficulty": info.get("difficulty", 0),
                "tags": tags
            })
    df = pd.DataFrame(champion_data)
    print(len(df))

    # Collect all unique tags
    all_tags = sorted({tag for tags in df["tags"] for tag in tags})
    print("All Tags:", all_tags)

    # One-hot encode tags
    for tag in all_tags:
        df[f"tag_{tag}"] = df["tags"].apply(lambda tags: 1 if tag in tags else 0)

    # Drop the original list column
    df = df.drop(columns=["tags"]).reset_index(drop=True)
    df["index"] = df.index
    return df


def get_champs_from_puuid(puuid: str, recent_k: int=30):
    matches = get_match_ids(puuid=puuid, count=recent_k)

    champs = []
    for match_id in matches:
        match = get_match(match_id=match_id, MATCH_REGION=MATCH_REGION, HEADERS=HEADERS).set_index("puuid")
        champs.append(match.loc[puuid]["championName"])
    
    return champs


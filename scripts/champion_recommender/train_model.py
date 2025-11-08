import os
import torch
import pandas as pd
from torch_geometric.data import Data
from collections import defaultdict, Counter
from utils import champion_node_rep, get_champs_from_puuid, get_puuid
import json


def cosine_sim(a, b):
    return torch.dot(a, b) / (torch.norm(a) * torch.norm(b) + 1e-9)


def clean_recent_champions(recent_champs, max_occurrences=5):
    """
    Ensures no champion appears more than `max_occurrences` times.
    Returns a filtered list preserving original order.
    """
    counts = Counter()
    to_remove = []
    for champ in recent_champs:
        counts[champ] += 1
        if counts[champ] > max_occurrences:
            to_remove.append(champ)
    return to_remove


def recommend_from_list(
        champion_list, 
        champ_node_data,
        graph, 
        champ_to_id,
        id_to_champ,
        feat_embeddings,
        top_k=5, 
        alpha=0.7, 
        filters={},
        max_occurences=2
    ):
    """
    Recommend top_k champions based on edge weights.
    exclude: set of champions to not include (to prevent overlaps)
    """
    allowed = filter_champions(champ_node_data, filters)
    combined_scores = defaultdict(float)

    for champ in champion_list:
        if champ not in champ_to_id:
            continue
        recs = combined_similarity(champ, graph, champ_to_id, id_to_champ, feat_embeddings, alpha=alpha, allowed=allowed)
        for r, score in recs.items() if isinstance(recs, dict) else []:
            combined_scores[r] += score
    # Sort aggregated scores
    sorted_recs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    to_remove = clean_recent_champions(champion_list, max_occurrences=max_occurences)

    return [c for c, _ in sorted_recs if c not in to_remove][:top_k]


def filter_champions(df, filters=None):
    """Return indices of champions satisfying feature constraints."""
    if filters is None:
        return set(df["championName"])

    filtered = df.copy()
    for key, value in filters.items():
        if key.startswith("tag_"):
            # categorical
            filtered = filtered[filtered[key] == value]

        elif isinstance(value, tuple):
            op, thresh = value
            if op == ">":
                filtered = filtered[filtered[key] > thresh]
            elif op == "<":
                filtered = filtered[filtered[key] < thresh]
            elif op == "==":
                filtered = filtered[filtered[key] == thresh]
    return set(filtered["championName"])


def combined_similarity(
        champion_name, 
        graph, 
        champ_to_id,
        id_to_champ,
        feat_embeddings,
        alpha=0.7, 
        allowed=set()
    ):
    """
    alpha: weight for graph similarity (0..1)
    (1-alpha) weight for feature similarity
    """
    champ_id = champ_to_id[champion_name]
    # Graph similarity (edge weight)
    graph_sims = {b: w for b, w in graph.get(champion_name, {}).items() if b in allowed}
    # print(graph_sims)
    # Feature similarity (cosine)
    feats = feat_embeddings[champ_id]
    cos_sims = {}
    for i, other in id_to_champ.items():
        if allowed and other not in allowed:
            continue
        cos_sims[other] = cosine_sim(feats, feat_embeddings[i]).item()

    # Combine: weighted sum
    combined = {}
    for champ in set(list(graph_sims.keys()) + list(cos_sims.keys())):
        g = graph_sims.get(champ, 0)
        f = cos_sims.get(champ, 0)
        combined[champ] = alpha * g + (1 - alpha) * f

    return combined


def save_graph_and_nodes(path="data/graph_data"):
    os.makedirs(path, exist_ok=True)
    with open(f"{path}/champion_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    champ_node_data.to_csv(f"{path}/champion_node_data.csv", index=False)

    with open(f"{path}/champion_mappings.json", "w", encoding="utf-8") as f:
        json.dump({"champ_to_id": champ_to_id, "id_to_champ": id_to_champ}, f, indent=2)
    return


def load_graph_and_nodes(path="data/graph_data"):
    with open(f"{path}/champion_graph.json", "r", encoding="utf-8") as f:
        graph = json.load(f)

    champ_node_data = pd.read_csv(f"{path}/champion_node_data.csv")

    with open(f"{path}/champion_mappings.json", "r", encoding="utf-8") as f:
        mappings = json.load(f)
        champ_to_id = mappings["champ_to_id"]
        id_to_champ = {int(k): v for k, v in mappings["id_to_champ"].items()}

    feat_embeddings = torch.tensor(champ_node_data.drop(columns=["championName", "index"]).values, dtype=torch.float)
    feat_embeddings = torch.nn.functional.normalize(feat_embeddings, dim=1)

    print(f"Loaded graph and {len(champ_node_data)} champions.")
    return graph, champ_node_data, champ_to_id, id_to_champ, feat_embeddings


if __name__=="__main__":
    # data cleaning
    # df = pd.read_csv("data/match_data/all_champion_matches.csv")
    # df["championName"] = df["championName"].str.replace(r"^Strawberry_?", "", regex=True)
    # df["championName"] = df["championName"].replace("FiddleSticks", "Fiddlesticks")
    # df = df[["puuid", "championName", "matchID"]]

    # map champions to ids
    # champ_node_data = champion_node_rep()
    # id_to_champ = {idx: name for idx, name in enumerate(champ_node_data["championName"].tolist())}
    # champ_to_id = {name: idx for idx, name in id_to_champ.items()}
    # df["championID"] = df["championName"].map(champ_to_id)

    # feat_embeddings = torch.tensor(champ_node_data.drop(columns=["championName", "index"]).values, dtype=torch.float)
    # feat_embeddings = torch.nn.functional.normalize(feat_embeddings, dim=1)

    # build graph and weights
    # edge_weights = defaultdict(int)
    # for _, group in df.groupby("puuid"):
    #     champs = group["championName"].tolist()  # or last N matches
    #     if len(champs) >= 2:
    #         for i in range(len(champs)):
    #             for j in range(i + 1, len(champs)):
    #                 edge_weights[(champs[i], champs[j])] += 1
    #                 edge_weights[(champs[j], champs[i])] += 1  # undirected
    
    # graph = defaultdict(dict)
    # for (a, b), w in edge_weights.items():
    #     graph[a][b] = w

    # for a in graph:
    #     max_w = max(graph[a].values())
    #     for b in graph[a]:
    #         graph[a][b] /= max_w

    graph, champ_node_data, champ_to_id, id_to_champ, feat_embeddings = load_graph_and_nodes()
    puuid = get_puuid("swaner", "NA1")
    recent_champs = get_champs_from_puuid(puuid)

    result = recommend_from_list(
        recent_champs,
        champ_node_data,
        graph,
        champ_to_id,
        id_to_champ,
        feat_embeddings,
        top_k=5,
        alpha=0.7,
    )
    print("recently played: ", recent_champs)
    print("recommendations: ", result)

# -*- coding: utf-8 -*-
"""
League of Legends Match Analysis Orchestrator

This module provides comprehensive analysis functions for League of Legends match data.
It calculates performance metrics, generates Chart.js-ready visualizations, and produces
a complete analysis JSON structure for frontend consumption.

Main Entry Point:
    analyze_match(match_id, match_data, timeline_data) - Runs full analysis suite
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from utils.logger import logger


# ==============================================================================
# 1. DATA PARSING FUNCTIONS
# ==============================================================================

def parse_match_info(match_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Parses the match data to extract key player information.
    
    Args:
        match_data: Match summary data from Riot API
        
    Returns:
        DataFrame with participantId, championName, and role columns
    """
    if not match_data or 'info' not in match_data or 'participants' not in match_data['info']:
        logger.warning("Match data missing expected 'info' or 'participants' keys.")
        return pd.DataFrame()

    participants_info = []
    for p in match_data['info']['participants']:
        participants_info.append({
            'participantId': p.get('participantId'),
            'championName': p.get('championName'),
            'role': p.get('teamPosition', p.get('lane', 'UNKNOWN'))
        })
    return pd.DataFrame(participants_info)


def parse_timeline_data(timeline_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Parses the timeline data, flattening the nested structure into a DataFrame.
    
    Args:
        timeline_data: Match timeline data from Riot API
        
    Returns:
        DataFrame with flattened timeline data suitable for time-series analysis
    """
    if not timeline_data or 'info' not in timeline_data or 'frames' not in timeline_data['info']:
        logger.warning("Timeline data missing expected 'info' or 'frames' keys.")
        return pd.DataFrame()

    flattened_frames = []
    for frame in timeline_data['info']['frames']:
        timestamp = frame.get('timestamp', 0)
        participant_frames = frame.get('participantFrames', {})

        for participant_id, p_data in participant_frames.items():
            flat_participant_data = {
                'timestamp': timestamp,
                'participantId': int(participant_id)
            }
            # Unpack nested dictionaries like 'championStats' and 'damageStats'
            for key, value in p_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_participant_data[f"{key}_{sub_key}"] = sub_value
                else:
                    flat_participant_data[key] = value
            flattened_frames.append(flat_participant_data)

    df = pd.DataFrame(flattened_frames)
    # Feature Engineering
    df['minutes'] = df['timestamp'] / 60000
    df = df[df['minutes'] >= 1]  # Start analysis from 1 minute to avoid initial anomalies
    df['teamId'] = df['participantId'].apply(lambda pid: 100 if pid <= 5 else 200)
    return df


# ==============================================================================
# 2. COMBAT POWER SCORE ANALYSIS
# ==============================================================================

def calculate_power_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the Combat Power Score for each player at each minute.
    
    This involves:
    1. Economic Power (Gold Differential)
    2. Offensive Power (AD, AP, Attack Speed)
    3. Defensive Power (Effective Health)
    4. Normalization and weighted aggregation
    
    Args:
        df: DataFrame with merged match and timeline data
        
    Returns:
        DataFrame with added 'power_score' column
    """
    if df.empty:
        logger.warning("Input DataFrame is empty, cannot calculate power score.")
        return df

    logger.debug("Starting Player Combat Power Score Calculation")

    # --- 1. Economic Power (Gold Differential) ---
    gold_pivot = df.pivot_table(
        index=['minutes', 'role'],
        columns='teamId',
        values='totalGold'
    ).reset_index()

    # Fill NaNs in case a role is missing for a team at a timestamp
    gold_pivot = gold_pivot.fillna(method='ffill').fillna(method='bfill')

    gold_pivot['gold_diff_100'] = gold_pivot[100] - gold_pivot[200]
    gold_pivot['gold_diff_200'] = gold_pivot[200] - gold_pivot[100]

    # Melt the data back to merge it with the main frame
    gold_diff_melted = pd.melt(
        gold_pivot,
        id_vars=['minutes', 'role'],
        value_vars=['gold_diff_100', 'gold_diff_200'],
        var_name='teamId_str',
        value_name='goldDifferential'
    )
    gold_diff_melted['teamId'] = gold_diff_melted['teamId_str'].apply(
        lambda x: int(x.split('_')[2])
    )
    df = pd.merge(
        df,
        gold_diff_melted[['minutes', 'role', 'teamId', 'goldDifferential']],
        on=['minutes', 'role', 'teamId']
    )

    # --- 2. Offensive Power ---
    df['offensive_score'] = (
        df['championStats_attackDamage'] * df['championStats_attackSpeed'] +
        df['championStats_abilityPower']
    )

    # --- 3. Defensive Power (Effective Health) ---
    df['defensive_score'] = df['championStats_health'] * (
        1 + (df['championStats_armor'] + df['championStats_magicResist']) / 200
    )

    # --- 4. Normalization ---
    scores_to_normalize = ['goldDifferential', 'offensive_score', 'defensive_score']
    for score in scores_to_normalize:
        min_val = df.groupby('minutes')[score].transform('min')
        max_val = df.groupby('minutes')[score].transform('max')
        df[f'norm_{score}'] = (df[score] - min_val) / (max_val - min_val)
        df[f'norm_{score}'] = df[f'norm_{score}'].fillna(0.5)

    # --- 5. Aggregation ---
    weights = {
        'econ': 0.45,
        'offense': 0.35,
        'defense': 0.20
    }
    df['power_score'] = (
        df['norm_goldDifferential'] * weights['econ'] +
        df['norm_offensive_score'] * weights['offense'] +
        df['norm_defensive_score'] * weights['defense']
    )

    logger.debug("Power Score calculation complete")
    return df


# ==============================================================================
# 3. END-OF-GAME PERFORMANCE SCORE (EPS) ANALYSIS
# ==============================================================================

def calculate_eps_with_distribution(match_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates the End-of-Game Performance Score (EPS) for each player.
    
    EPS breaks down into three components:
    - Combat Score (40%): KDA, kill participation, damage share
    - Economic Score (30%): GPM, CSM, damage per gold
    - Objective Score (30%): Vision, objective damage, turret damage
    
    Args:
        match_data: Match summary data from Riot API
        
    Returns:
        DataFrame with EPS scores and component breakdowns
    """
    if not match_data:
        logger.warning("Match data not available. Cannot calculate EPS.")
        return pd.DataFrame()

    logger.debug("Calculating EPS with Contribution Breakdown")

    # 1. Create DataFrame from participant data
    df = pd.DataFrame(match_data['info']['participants'])
    game_duration_minutes = match_data['info']['gameDuration'] / 60

    # 2. Calculate Team-Level Totals for context
    team_stats = df.groupby('teamId').agg(
        team_kills=('kills', 'sum'),
        team_damage_to_champions=('totalDamageDealtToChampions', 'sum'),
        team_damage_to_objectives=('damageDealtToObjectives', 'sum')
    ).reset_index()
    df = pd.merge(df, team_stats, on='teamId')

    # 3. Calculate Base Metrics for EPS components
    df['kda'] = (df['kills'] + df['assists']) / df['deaths'].apply(lambda d: max(d, 1))
    df['kill_participation'] = (df['kills'] + df['assists']) / df['team_kills']
    df['damage_share'] = df['totalDamageDealtToChampions'] / df['team_damage_to_champions']
    df['gpm'] = df['goldEarned'] / game_duration_minutes
    df['cspm'] = (df['totalMinionsKilled'] + df['neutralMinionsKilled']) / game_duration_minutes
    df['damage_per_gold'] = df['totalDamageDealtToChampions'] / df['goldEarned'].apply(lambda g: max(g, 1))
    df['objective_damage_share'] = df['damageDealtToObjectives'] / df['team_damage_to_objectives'].apply(lambda o: max(o, 1))
    df['vspm'] = df['visionScore'] / game_duration_minutes

    # 4. Normalize Metrics
    metrics_to_normalize = [
        'kda', 'kill_participation', 'damage_share', 'gpm', 'cspm',
        'damage_per_gold', 'objective_damage_share', 'vspm', 'damageDealtToTurrets'
    ]
    for metric in metrics_to_normalize:
        min_val, max_val = df[metric].min(), df[metric].max()
        if (max_val - min_val) > 0:
            df[f'norm_{metric}'] = (df[metric] - min_val) / (max_val - min_val)
        else:
            df[f'norm_{metric}'] = 0.5

    # 5. Calculate Weighted Sub-Scores
    df['combat_score'] = (df['norm_kda'] + df['norm_kill_participation'] + df['norm_damage_share']) / 3
    df['economic_score'] = (df['norm_gpm'] + df['norm_cspm'] + df['norm_damage_per_gold']) / 3

    def get_objective_score(row):
        role = row['teamPosition']
        if role in ['UTILITY', 'JUNGLE']:
            return (row['norm_vspm'] * 0.6) + (row['norm_objective_damage_share'] * 0.4)
        else:
            return (row['norm_damageDealtToTurrets'] * 0.6) + (row['norm_objective_damage_share'] * 0.4)
    df['objective_score'] = df.apply(get_objective_score, axis=1)

    # 6. Calculate Contribution of Each Component to the Final Score
    weights = {'combat': 0.40, 'economic': 0.30, 'objective': 0.30}

    df['Combat'] = df['combat_score'] * weights['combat'] * 100
    df['Economic'] = df['economic_score'] * weights['economic'] * 100
    df['Objective'] = df['objective_score'] * weights['objective'] * 100

    # The final EPS is the sum of these contributions
    df['EPS'] = df['Combat'] + df['Economic'] + df['Objective']

    # 7. Prepare Final Output
    df_result = df[[
        'championName', 'teamPosition', 'win', 'Combat', 'Economic', 'Objective', 'EPS'
    ]].sort_values('EPS', ascending=False).reset_index(drop=True)

    return df_result.round(1)


# ==============================================================================
# 4. CHART.JS OUTPUT GENERATION
# ==============================================================================

def _build_participant_lookup(match_data: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """Builds a lookup dictionary for participant metadata."""
    participants = match_data.get('info', {}).get('participants', [])
    lookup = {}
    for p in participants:
        lookup[p.get('participantId', len(lookup) + 1)] = {
            'teamId': p.get('teamId', 100),
            'championName': p.get('championName', 'Unknown'),
            'teamPosition': p.get('teamPosition', 'UNKNOWN'),
            'summonerName': p.get('summonerName', p.get('riotIdGameName', 'Player'))
        }
    return lookup


def _compute_power_score_chart(
    match_data: Dict[str, Any],
    timeline_data: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[int, float]]:
    """
    Computes power score timeline chart data.
    
    Returns:
        Tuple of (chart_config, power_efficiency_dict)
    """
    participant_lookup = _build_participant_lookup(match_data)

    rows = []
    frames = timeline_data.get('info', {}).get('frames', [])
    for frame in frames:
        ts = frame.get('timestamp', 0)
        minutes = int(max(0, round(ts / 60000)))
        pframes = frame.get('participantFrames', {})
        for pid_str, pframe in pframes.items():
            try:
                pid = int(pid_str)
            except Exception:
                pid = pframe.get('participantId', None) or 0
            meta = participant_lookup.get(pid, {})
            champ_stats = pframe.get('championStats', {}) or {}
            rows.append({
                'minutes': minutes,
                'participantId': pid,
                'teamId': meta.get('teamId', 100),
                'role': meta.get('teamPosition', 'UNKNOWN'),
                'playerLabel': f"{meta.get('championName', 'Unknown')} ({meta.get('teamPosition', 'UNKNOWN')})",
                'totalGold': pframe.get('totalGold', 0),
                'championStats_attackDamage': champ_stats.get('attackDamage', 0),
                'championStats_attackSpeed': champ_stats.get('attackSpeed', 0),
                'championStats_abilityPower': champ_stats.get('abilityPower', 0),
                'championStats_health': champ_stats.get('health', 0),
                'championStats_armor': champ_stats.get('armor', 0),
                'championStats_magicResist': champ_stats.get('magicResist', 0)
            })

    if not rows:
        return {
            'type': 'line',
            'data': {'labels': [], 'datasets': []},
            'options': {'responsive': True, 'plugins': {'title': {'text': 'Power Score Over Time'}}}
        }, {}

    df = pd.DataFrame(rows)
    df = calculate_power_score(df)

    # Build Chart.js datasets
    minutes_labels = sorted(df['minutes'].unique().tolist())

    # Team colors
    team_colors = {
        100: ['#1E88E5', '#42A5F5', '#64B5F6', '#1976D2', '#90CAF9'],
        200: ['#E53935', '#EF5350', '#E57373', '#C62828', '#FF8A80']
    }

    datasets = []
    for pid, group in df.groupby('participantId'):
        meta = participant_lookup.get(pid, {})
        team_id = meta.get('teamId', 100)
        team_palette = team_colors[100] if team_id == 100 else team_colors[200]
        color = team_palette[(pid - 1) % len(team_palette)]
        series = group.sort_values('minutes')[['minutes', 'power_score']]
        series = series.drop_duplicates(subset=['minutes'], keep='last')
        value_by_min = {int(m): float(v) for m, v in zip(series['minutes'], series['power_score'])}
        data_points = [round(value_by_min.get(m, None) or 0.0, 4) for m in minutes_labels]
        datasets.append({
            'label': f"{meta.get('championName', 'Unknown')} ({meta.get('teamPosition', 'UNKNOWN')})",
            'data': data_points,
            'borderColor': color,
            'fill': False
        })

    chart = {
        'type': 'line',
        'data': {
            'labels': minutes_labels,
            'datasets': datasets
        },
        'options': {
            'responsive': True,
            'plugins': {'title': {'text': 'Power Score Over Time'}}
        }
    }

    # Also compute gold efficiency baseline (power per 1k gold) here for reuse
    df['power_per_1k_gold'] = df.apply(
        lambda r: (r['power_score'] / (r['totalGold'] / 1000)) if r['totalGold'] else 0.0,
        axis=1
    )
    avg_eff = df.groupby('participantId')['power_per_1k_gold'].mean().to_dict()

    return chart, avg_eff


def _build_eps_chart(match_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """
    Builds EPS breakdown chart data.
    
    Returns:
        Tuple of (chart_config, eps_scores_dict)
    """
    eps_df = calculate_eps_with_distribution(match_data)
    if eps_df is None or eps_df.empty:
        return {
            'type': 'bar',
            'data': {'labels': [], 'datasets': []},
            'options': {'indexAxis': 'y', 'scales': {'x': {'stacked': True}, 'y': {'stacked': True}}}
        }, {}

    # Labels: player names (prefer summonerName if available)
    participants = match_data.get('info', {}).get('participants', [])
    name_by_champion = {
        p.get('championName'): p.get('summonerName', p.get('riotIdGameName', p.get('championName')))
        for p in participants
    }

    eps_sorted = eps_df.sort_values('EPS', ascending=False)
    labels = [name_by_champion.get(ch, ch) for ch in eps_sorted['championName'].tolist()]

    datasets = [
        {'label': 'Combat Score', 'data': eps_sorted['Combat'].round(1).tolist(), 'backgroundColor': '#e74c3c'},
        {'label': 'Economic Score', 'data': eps_sorted['Economic'].round(1).tolist(), 'backgroundColor': '#f1c40f'},
        {'label': 'Objective Score', 'data': eps_sorted['Objective'].round(1).tolist(), 'backgroundColor': '#3498db'}
    ]

    chart = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        'options': {
            'indexAxis': 'y',
            'scales': {'x': {'stacked': True}, 'y': {'stacked': True}}
        }
    }

    eps_scores_raw = {
        row['championName']: float(row['EPS'])
        for _, row in eps_sorted[['championName', 'EPS']].iterrows()
    }

    return chart, eps_scores_raw


def _build_gold_efficiency_chart(
    match_data: Dict[str, Any],
    power_eff_by_pid: Dict[int, float]
) -> Dict[str, Any]:
    """Builds gold efficiency chart data."""
    if not power_eff_by_pid:
        return {
            'type': 'bar',
            'data': {'labels': [], 'datasets': []}
        }

    participants = match_data.get('info', {}).get('participants', [])
    by_pid_meta = {p.get('participantId'): p for p in participants}

    # Compute relative percentages
    values = list(power_eff_by_pid.values())
    mean_val = (sum(values) / len(values)) if values else 1.0

    labels = []
    data_vals = []
    colors = []
    for pid, val in power_eff_by_pid.items():
        meta = by_pid_meta.get(pid, {})
        labels.append(meta.get('summonerName', meta.get('riotIdGameName', meta.get('championName', f'P{pid}'))))
        pct = 100.0 * (val / mean_val) if mean_val else 0.0
        data_vals.append(round(pct, 1))
        colors.append('#3498db' if meta.get('teamId', 100) == 100 else '#e74c3c')

    chart = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [
                {'label': 'Gold Efficiency %', 'data': data_vals, 'backgroundColor': colors}
            ]
        }
    }
    return chart


# ==============================================================================
# 5. MAIN ANALYSIS ORCHESTRATOR
# ==============================================================================

def analyze_match(
    match_id: str,
    match_data: Dict[str, Any],
    timeline_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main orchestrator function that runs the full suite of match analysis.
    
    This function coordinates all analysis components:
    - Power Score Timeline (requires both match_data and timeline_data)
    - EPS Breakdown (requires match_data only)
    - Gold Efficiency (requires both match_data and timeline_data)
    
    Args:
        match_id: Unique match identifier
        match_data: Match summary data from Riot API (required)
        timeline_data: Match timeline data from Riot API (optional, but required for some analyses)
        
    Returns:
        Dictionary containing:
        - matchId: The match ID
        - charts: Chart.js configuration objects for all visualizations
        - rawStats: Raw statistical data for programmatic access
        
    Raises:
        ValueError: If match_data is None or invalid
    """
    if not match_data:
        raise ValueError("match_data is required for analysis")
    
    logger.info(f"Starting analysis for match {match_id}")
    
    result = {
        'matchId': match_id,
        'charts': {},
        'rawStats': {}
    }
    
    # Always compute EPS (only needs match_data)
    try:
        logger.debug("Computing EPS breakdown...")
        eps_chart, eps_raw_scores = _build_eps_chart(match_data)
        result['charts']['epsBreakdown'] = eps_chart
        result['rawStats']['epsScores'] = eps_raw_scores
    except Exception as e:
        logger.error(f"Error computing EPS breakdown: {e}")
        result['charts']['epsBreakdown'] = {
            'type': 'bar',
            'data': {'labels': [], 'datasets': []},
            'options': {'indexAxis': 'y', 'scales': {'x': {'stacked': True}, 'y': {'stacked': True}}}
        }
        result['rawStats']['epsScores'] = {}
    
    # Compute timeline-based analyses if timeline_data is available
    if timeline_data:
        try:
            logger.debug("Computing power score timeline...")
            power_chart, power_eff = _compute_power_score_chart(match_data, timeline_data)
            result['charts']['powerScoreTimeline'] = power_chart
            result['rawStats']['powerEfficiency'] = power_eff
            
            logger.debug("Computing gold efficiency...")
            gold_eff_chart = _build_gold_efficiency_chart(match_data, power_eff)
            result['charts']['goldEfficiency'] = gold_eff_chart
        except Exception as e:
            logger.error(f"Error computing timeline-based analyses: {e}")
            result['charts']['powerScoreTimeline'] = {
                'type': 'line',
                'data': {'labels': [], 'datasets': []},
                'options': {'responsive': True, 'plugins': {'title': {'text': 'Power Score Over Time'}}}
            }
            result['charts']['goldEfficiency'] = {
                'type': 'bar',
                'data': {'labels': [], 'datasets': []}
            }
            result['rawStats']['powerEfficiency'] = {}
    else:
        logger.warning(f"Timeline data not provided for match {match_id}. Skipping timeline-based analyses.")
        result['charts']['powerScoreTimeline'] = {
            'type': 'line',
            'data': {'labels': [], 'datasets': []},
            'options': {'responsive': True, 'plugins': {'title': {'text': 'Power Score Over Time'}}}
        }
        result['charts']['goldEfficiency'] = {
            'type': 'bar',
            'data': {'labels': [], 'datasets': []}
        }
        result['rawStats']['powerEfficiency'] = {}
    
    logger.info(f"Analysis complete for match {match_id}")
    return result


# ==============================================================================
# 6. LEGACY COMPATIBILITY
# ==============================================================================

def generate_match_analysis(match_id: str, match_info_data: Dict[str, Any], timeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function name for backward compatibility.
    
    This is an alias for analyze_match() that maintains the original function signature.
    """
    return analyze_match(match_id, match_info_data, timeline_data)


# ==============================================================================
# 7. STANDALONE EXECUTION
# ==============================================================================

if __name__ == '__main__':
    # For testing/development: can be run with preloaded data
    import sys
    
    if len(sys.argv) > 1:
        # If JSON file paths provided as arguments
        match_file = sys.argv[1] if len(sys.argv) > 1 else None
        timeline_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if match_file and timeline_file:
            with open(match_file, 'r') as f:
                match_data = json.load(f)
            with open(timeline_file, 'r') as f:
                timeline_data = json.load(f)
            
            match_id = match_data.get('metadata', {}).get('matchId', 'UNKNOWN_MATCH_ID')
            result = analyze_match(match_id, match_data, timeline_data)
            print(json.dumps(result, indent=2))
        else:
            print("Usage: python league_of_legends_hackathon.py <match_file.json> <timeline_file.json>")
    else:
        print("Match Analysis Orchestrator")
        print("Use analyze_match(match_id, match_data, timeline_data) to run analysis")

"""Manual labeling app for mechanics description similarity ratings.

This script loads the mechanics_descriptions.json file, generates random pairs of abilities from different champions,
and prompts the user to rate their similarity based on the LLM-generated mechanics descriptions.

Responses are saved to a CSV file for evaluating the quality of mechanics descriptions.
"""
import json
from pathlib import Path
import argparse
import itertools
import csv
import random
import os

OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'output'
MECHANICS_PATH = OUTPUT_DIR / 'mechanics_descriptions.json'
LABELS_CSV = OUTPUT_DIR / 'mechanics_similarity_labels.csv'


def load_existing_labels(csv_path):
    """Load already labeled pairs to avoid duplicates."""
    labeled = set()
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 6:
                    pair = (row[0], row[1], row[2], row[3], row[4], row[5])
                    labeled.add(pair)
    return labeled


def extract_mechanics_abilities(mechanics_data):
    """Extract all abilities with mechanics descriptions into a flat list."""
    abilities = []
    
    for champ in mechanics_data:
        champ_name = champ.get('name')
        for ability in champ.get('abilities', []):
            abilities.append({
                'champion': champ_name,
                'type': ability.get('type'),
                'name': ability.get('name'),
                'mechanics_description': ability.get('mechanics_description', '')
            })
    
    return abilities


def extract_mechanics_descriptions(mechanics_data):
    """Extract all abilities with mechanics descriptions into a flat list."""
    abilities = []

    for champ in mechanics_data:
        champ_name = champ.get('name')
        for ability in champ.get('abilities', []):
            abilities.append({
                'champion': champ_name,
                'type': ability.get('type'),
                'name': ability.get('name'),
                'original_description': ability.get('original_description', ''),
                'mechanics_description': ability.get('mechanics_description', '')
            })

    return abilities


def main(limit=None, shuffle=True):
    # Load mechanics data
    with open(MECHANICS_PATH, 'r', encoding='utf-8') as fh:
        mechanics_data = json.load(fh)
    
    # Extract abilities
    abilities = extract_mechanics_abilities(mechanics_data)
    print(f"Loaded {len(abilities)} abilities with mechanics descriptions")
    
    # Generate pairs
    all_pairs = list(itertools.combinations(abilities, 2))
    pairs = [(a, b) for a, b in all_pairs if a['champion'] != b['champion']]
    print(f"Generated {len(pairs)} unique pairs")
    
    if shuffle:
        random.shuffle(pairs)
    
    # Load existing labels
    labeled = load_existing_labels(LABELS_CSV)
    print(f"Found {len(labeled)} already labeled pairs")
    
    # Prepare CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_exists = LABELS_CSV.exists()
    with open(LABELS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not csv_exists:
            writer.writerow(['champ1', 'ability1_type', 'ability1_name', 'champ2', 'ability2_type', 'ability2_name', 'score', 'explanation'])
    
    # Labeling loop
    count = 0
    for a, b in pairs:
        if limit and count >= limit:
            break
        
        pair_key = (a['champion'], a['type'], a['name'], b['champion'], b['type'], b['name'])
        if pair_key in labeled:
            continue
        
        print(f"\n--- Pair {count + 1} ---")
        print(f"Ability 1: {a['champion']} {a['type']} - {a['name']}")
        print(f"Mechanics: {a['mechanics_description']}")
        print()
        print(f"Ability 2: {b['champion']} {b['type']} - {b['name']}")
        print(f"Mechanics: {b['mechanics_description']}")
        print()
        
        while True:
            user_input = input("Similarity score (0.0-1.0), 's' to skip, 'q' to quit: ").strip().lower()
            if user_input == 'q':
                print("Quitting...")
                return
            elif user_input == 's':
                print("Skipping this pair.")
                break
            try:
                score = float(user_input)
                if 0.0 <= score <= 1.0:
                    break
                else:
                    print("Score must be between 0.0 and 1.0")
            except ValueError:
                print("Invalid input, try again")
        
        if user_input == 's':
            count += 1
            continue
        
        explanation = input("Explanation (1-2 sentences): ").strip()
        
        # Save
        with open(LABELS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                a['champion'], a['type'], a['name'],
                b['champion'], b['type'], b['name'],
                score, explanation
            ])
        
        labeled.add(pair_key)
        count += 1
        print(f"Saved! ({count} labeled so far)")
        
        cont = input("Continue? (y/n): ").strip().lower()
        if cont != 'y':
            break
    
    print(f"\nLabeling complete. {count} new pairs labeled. Total in CSV: {len(labeled)}")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manual labeling of mechanics description similarities')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of pairs to label')
    parser.add_argument('--no-shuffle', action='store_true', help='Do not shuffle pairs (label in order)')
    args = parser.parse_args()
    
    main(limit=args.limit, shuffle=not args.no_shuffle)
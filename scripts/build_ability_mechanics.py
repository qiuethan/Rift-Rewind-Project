"""
Script that uses original description + LLM to build ability mechanics descriptions. 
"""
import json
from pathlib import Path
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Add parent directory to path to import openrouter_helper
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from openrouter_helper import get_openrouter_response

DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'champion_data'
OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'output'
OUT_PATH = OUTPUT_DIR / 'ability_mechanics.json'

SYSTEM_PROMPT = (
    "You are an expert on League of Legends champion abilities. Provide concise, accurate descriptions of how abilities work mechanically."
)


def build_mechanics_prompt(champion_name: str, ability_name: str, ability_type: str, original_desc: str) -> str:
    """Build prompt for getting mechanical description of an ability."""
    prompt = f"""
Describe the League of Legends ability "{ability_name}" ({ability_type}) for champion {champion_name}.

Focus on:
1. How to hit/use the ability: point and click, skillshot (linear/cone/circular), dash, toggle, auto-target, etc.
2. How it is used: offensively (damage, burst), defensively (shield, heal), both, utility (CC, buff, debuff), etc.

Here is the original description of the ability. If it does not describe mechanics well, improve upon it. {original_desc}

Provide a concise 1-2 sentence description emphasizing mechanics and usage patterns.
"""
    return prompt.strip()


def clean_description(desc: str) -> str:
    """Clean description by removing template placeholders."""
    if not desc:
        return desc
    # Remove common placeholders
    desc = desc.replace('{{ spellmodifierdescriptionappend }}', '')
    desc = desc.replace('{{ Spell_AkshanW_Tooltip_{{ gamemodeinteger }} }}', '')
    # Add more if needed
    return desc.strip()


def extract_champion_info(path: Path) -> list:
    try:
        raw = json.loads(path.read_text())
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return []

    # Common Riot/DataDragon format: {"data": {"ChampionName": {...}}}
    champ = None
    
    # First, check if there's a 'data' key with nested champion
    if isinstance(raw, dict) and 'data' in raw:
        data = raw['data']
        if isinstance(data, dict):
            # Get the first (and usually only) champion in the data dict
            for champion_key, champion_data in data.items():
                if isinstance(champion_data, dict) and ('spells' in champion_data or 'passive' in champion_data):
                    champ = champion_data
                    break
    
    # Fallback: champion data at top level
    if champ is None and isinstance(raw, dict) and 'name' in raw and ('spells' in raw or 'passive' in raw):
        champ = raw
    
    # Another fallback: try common nesting patterns
    if champ is None and isinstance(raw, dict):
        for key, val in raw.items():
            if isinstance(val, dict) and 'name' in val and ('spells' in val or 'passive' in val):
                champ = val
                break

    if champ is None:
        print(f"Could not locate champion dict in {path}. Skipping.")
        return []

    name = champ.get('name') or champ.get('id') or path.stem

    abilities = []

    # Passive extraction
    p = champ.get('passive') or champ.get('passivePassive') or champ.get('Passive')
    if isinstance(p, dict):
        desc = p.get('description') or ''
        tooltip = p.get('tooltip') or p.get('sanitizedDescription') or ''
        # Concatenate description and tooltip if both exist
        combined_desc = f"{desc} {tooltip}".strip() if desc and tooltip else (desc or tooltip)
        if combined_desc:
            abilities.append({
                'champion': name,
                'type': 'Passive',
                'name': p.get('name', 'Passive'),
                'original_description': clean_description(combined_desc)
            })
    elif isinstance(p, str) and p:
        abilities.append({
            'champion': name,
            'type': 'Passive',
            'name': 'Passive',
            'original_description': clean_description(p)
        })

    # Spells extraction (Q/W/E/R or ability list)
    spells = champ.get('spells') or champ.get('Abilities') or champ.get('ability')
    if isinstance(spells, list):
        spell_types = ['Q', 'W', 'E', 'R']
        for i, s in enumerate(spells):
            if isinstance(s, dict):
                desc = s.get('description') or ''
                tooltip = s.get('tooltip') or s.get('sanitizedDescription') or ''
                # Concatenate description and tooltip if both exist
                combined_desc = f"{desc} {tooltip}".strip() if desc and tooltip else (desc or tooltip)
                if combined_desc:
                    ability_type = spell_types[i] if i < len(spell_types) else f'Ability {i+1}'
                    abilities.append({
                        'champion': name,
                        'type': ability_type,
                        'name': s.get('name', f'{ability_type} Ability'),
                        'original_description': clean_description(combined_desc)
                    })
            elif isinstance(s, str) and s:
                ability_type = spell_types[i] if i < len(spell_types) else f'Ability {i+1}'
                abilities.append({
                    'champion': name,
                    'type': ability_type,
                    'name': f'{ability_type} Ability',
                    'original_description': clean_description(s)
                })

    return abilities


def extract_abilities_from_champions(champions_data):
    """Extract all abilities from the champions JSON."""
    abilities = []
    
    for champ_key, champ_data in champions_data.items():
        champ_name = champ_data.get('name', champ_key)
        
        # Passive
        passive = champ_data.get('passive')
        if passive and isinstance(passive, dict):
            desc = passive.get('description') or 'No description available'
            abilities.append({
                'champion': champ_name,
                'type': 'Passive',
                'name': passive.get('name', 'Passive'),
                'original_description': desc
            })
        
        # Spells
        spells = champ_data.get('spells', [])
        spell_types = ['Q', 'W', 'E', 'R']
        for i, spell in enumerate(spells):
            if isinstance(spell, dict):
                desc = spell.get('description') or 'No description available'
                ability_type = spell_types[i] if i < len(spell_types) else f'Ability{i+1}'
                abilities.append({
                    'champion': champ_name,
                    'type': ability_type,
                    'name': spell.get('name', f'{ability_type} Ability'),
                    'original_description': desc
                })
    
def build_mechanics_index(data_dir: Path, out_path: Path, model_name: str, num_threads: int = 4, limit: int = None):
    # Load champions data from individual files
    abilities = []
    champion_files = list(data_dir.glob('*.json'))
    print(f"Found {len(champion_files)} champion files")
    
    for path in champion_files:
        champ_abilities = extract_champion_info(path)
        abilities.extend(champ_abilities)
    
    print(f"Found {len(abilities)} abilities across {len(champion_files)} champions")
    
    if limit:
        abilities = abilities[:limit]
        print(f"Limited to first {limit} abilities")
    
    # Prepare output structure
    mechanics_data = {}
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    def process_ability(ability):
        """Process a single ability and return the result."""
        prompt = build_mechanics_prompt(
            ability['champion'],
            ability['name'],
            ability['type'],
            ability['original_description']
        )
        
        try:
            response = get_openrouter_response(model_name, prompt, SYSTEM_PROMPT)
            mechanics_desc = response.strip()
        except Exception as e:
            print(f"Error querying {ability['champion']} {ability['type']}: {e}")
            mechanics_desc = f"Error: {e}"
        
        return {
            'champion': ability['champion'],
            'type': ability['type'],
            'name': ability['name'],
            'mechanics_description': mechanics_desc,
            'original_description': ability['original_description']
        }
    
    # Process abilities in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(process_ability, ability): ability for ability in abilities}
        
        with tqdm(total=len(abilities), desc="Querying ability mechanics", unit="ability") as pbar:
            for future in as_completed(futures):
                result = future.result()
                champ = result['champion']
                if champ not in mechanics_data:
                    mechanics_data[champ] = {
                        'name': champ,
                        'abilities': []
                    }
                
                mechanics_data[champ]['abilities'].append({
                    'type': result['type'],
                    'name': result['name'],
                    'mechanics_description': result['mechanics_description'],
                    'original_description': result['original_description']
                })
                
                pbar.update(1)
    
    # Convert to list format like ability_index.json
    output_list = []
    for champ_data in mechanics_data.values():
        output_list.append({
            'name': champ_data['name'],
            'abilities': champ_data['abilities']
        })
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
    
    print(f"Wrote mechanics for {len(output_list)} champions to {out_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build ability mechanics index using OpenRouter')
    parser.add_argument('--model', default='google/gemini-2.5-flash-lite', help='Model name to use')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of abilities to process (for testing)')
    parser.add_argument('--out', type=str, default=str(OUT_PATH), help='Output JSON path')
    parser.add_argument('--num-threads', type=int, default=4, help='Number of concurrent API calls')
    args = parser.parse_args()
    
    build_mechanics_index(DATA_DIR, Path(args.out), args.model, num_threads=args.num_threads, limit=args.limit)
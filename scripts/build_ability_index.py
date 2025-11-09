"""Build an ability index from JSON champion files.

This script walks `data/champion_data/` and extracts for each champion:
- champion id/name
- passive (name + description)
- spells: list of (name + description)

It writes `data/ability_index.json` with a list of champion entries.

This script is intentionally tolerant of small schema differences across champion JSONs
from various sources. It tries a few reasonable keys and falls back gracefully.
"""
from pathlib import Path
import json
import argparse

DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'champion_data'
OUT_PATH = Path(__file__).resolve().parents[1] / 'output' / 'ability_index.json'


def clean_description(desc: str) -> str:
    """Clean description by removing template placeholders."""
    if not desc:
        return desc
    # Remove common placeholders
    desc = desc.replace('{{ spellmodifierdescriptionappend }}', '')
    desc = desc.replace('{{ Spell_AkshanW_Tooltip_{{ gamemodeinteger }} }}', '')
    # Add more if needed
    return desc.strip()


def extract_champion_info(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text())
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return None

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
        return None

    name = champ.get('name') or champ.get('id') or path.stem
    tags = champ.get('tags') or []

    # Passive extraction
    passive = None
    p = champ.get('passive') or champ.get('passivePassive') or champ.get('Passive')
    if isinstance(p, dict):
        desc = p.get('description') or ''
        tooltip = p.get('tooltip') or p.get('sanitizedDescription') or ''
        # Concatenate description and tooltip if both exist
        combined_desc = f"{desc} {tooltip}".strip() if desc and tooltip else (desc or tooltip)
        passive = {
            'name': p.get('name'),
            'description': clean_description(combined_desc)
        }
    elif isinstance(p, str):
        passive = {'name': None, 'description': p}

    # Spells extraction (Q/W/E/R or ability list)
    spells_out = []
    spells = champ.get('spells') or champ.get('Abilities') or champ.get('ability')
    if isinstance(spells, list):
        for s in spells:
            if isinstance(s, dict):
                desc = s.get('description') or ''
                tooltip = s.get('tooltip') or s.get('sanitizedDescription') or ''
                # Concatenate description and tooltip if both exist
                combined_desc = f"{desc} {tooltip}".strip() if desc and tooltip else (desc or tooltip)
                spells_out.append({
                    'name': s.get('name'),
                    'description': clean_description(combined_desc)
                })
            elif isinstance(s, str):
                spells_out.append({'name': None, 'description': s})

    # Fallback: sometimes abilities are stored under 'data' -> champion key
    if not spells_out:
        # search for lists of dicts that look like spells
        def looks_like_spell_list(obj):
            if not isinstance(obj, list):
                return False
            for item in obj:
                if not isinstance(item, dict):
                    return False
                if 'description' in item or 'tooltip' in item or 'name' in item:
                    return True
            return False

        for v in champ.values():
            if looks_like_spell_list(v):
                for s in v:
                    spells_out.append({
                        'name': s.get('name'),
                        'description': clean_description(s.get('description') or s.get('tooltip'))
                    })
                break

    entry = {
        'file': path.name,
        'name': name,
        'tags': tags,
        'passive': passive,
        'spells': spells_out
    }

    return entry


def build_index(src_dir: Path, out_path: Path):
    src = src_dir
    out = out_path
    out.parent.mkdir(parents=True, exist_ok=True)

    entries = []
    for p in sorted(src.glob('*.json')):
        entry = extract_champion_info(p)
        if entry:
            entries.append(entry)

    out.write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    print(f"Wrote {len(entries)} champions to {out}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build ability_index.json from champion_data JSON files')
    parser.add_argument('--src', type=str, default=str(DATA_DIR), help='Path to champion_data directory')
    parser.add_argument('--out', type=str, default=str(OUT_PATH), help='Output json path')
    args = parser.parse_args()

    build_index(Path(args.src), Path(args.out))

#!/usr/bin/env python3
"""
Import high-confidence cooperatives from Iowa SoS data into verified list.

These are cooperatives registered with official cooperative corporation types,
so they don't need similarity scoring - they're definitively cooperatives.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SOS_CANDIDATES_FILE = DATA_DIR / "sos_candidates.json"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"

# Corporation types that definitively indicate a cooperative
COOP_CORP_TYPES = [
    "CO-OP NON STOCK",
    "CO-OP STOCK",
    "DOMESTIC COOPERATIVE",
    "CO-OP STOCK VALUE ADDED",
]

# High-confidence name patterns
HIGH_CONF_PATTERNS = [
    'rural electric',
    'electric cooperative',
    'power cooperative',
    'telephone cooperative',
    'telecom cooperative',
    'farmers cooperative',
    'cooperative elevator',
    'cooperative exchange',
    'credit union',
    'food co-op',
    'food cooperative',
]


def determine_category(name: str, hint: str) -> str:
    """Determine category from name and hint."""
    name_lower = name.lower()

    if 'electric' in name_lower or 'power' in name_lower:
        return 'electric'
    elif 'telephone' in name_lower or 'telecom' in name_lower or 'communications' in name_lower:
        return 'telecom'
    elif 'credit union' in name_lower:
        return 'credit'
    elif any(kw in name_lower for kw in ['farm', 'grain', 'elevator', 'seed', 'agri', 'dairy', 'livestock']):
        return 'agricultural'
    elif 'food' in name_lower or 'market' in name_lower or 'grocery' in name_lower:
        return 'food'
    elif 'housing' in name_lower or 'home' in name_lower:
        return 'housing'
    elif hint != 'other':
        return hint
    else:
        return 'other'


def main():
    print("Loading data...")

    with open(SOS_CANDIDATES_FILE) as f:
        sos_candidates = json.load(f)

    with open(LABELED_DATA_PATH) as f:
        labeled_data = json.load(f)

    # Get existing verified names to avoid duplicates
    verified_names = set()
    for c in labeled_data['verified_cooperatives']:
        verified_names.add(c['name'].lower().strip())

    print(f"SoS candidates: {len(sos_candidates)}")
    print(f"Currently verified: {len(labeled_data['verified_cooperatives'])}")

    # Filter to high-confidence cooperatives
    high_conf = []
    for c in sos_candidates:
        # By corporation type
        if c.get('corp_type') in COOP_CORP_TYPES:
            high_conf.append(c)
            continue

        # By name pattern
        name_lower = c['name'].lower()
        if any(p in name_lower for p in HIGH_CONF_PATTERNS):
            high_conf.append(c)

    print(f"High-confidence cooperatives: {len(high_conf)}")

    # Get max ID
    max_id = max(c['id'] for c in labeled_data['verified_cooperatives'])

    # Add to verified list
    added = 0
    skipped_dup = 0

    for c in high_conf:
        # Check for duplicate
        if c['name'].lower().strip() in verified_names:
            skipped_dup += 1
            continue

        max_id += 1
        category = determine_category(c['name'], c.get('category_hint', 'other'))

        new_coop = {
            'id': max_id,
            'name': c['name'],
            'category': category,
            'website': None,  # No website from SoS data
            'location': c.get('location', 'Iowa'),
            'verified_date': datetime.now().isoformat(),
            'source': 'iowa_sos',
            'corp_type': c.get('corp_type'),
            'corp_number': c.get('corp_number'),
        }

        labeled_data['verified_cooperatives'].append(new_coop)
        verified_names.add(c['name'].lower().strip())
        added += 1

    # Update stats
    labeled_data['stats']['total_verified'] = len(labeled_data['verified_cooperatives'])
    labeled_data['metadata']['last_updated'] = datetime.now().isoformat()

    # Save
    print(f"\nAdded: {added}")
    print(f"Skipped (duplicate): {skipped_dup}")
    print(f"New total verified: {labeled_data['stats']['total_verified']}")

    with open(LABELED_DATA_PATH, 'w') as f:
        json.dump(labeled_data, f, indent=2)

    print(f"\nSaved to {LABELED_DATA_PATH}")

    # Category breakdown of new additions
    from collections import Counter
    new_cats = Counter()
    for c in labeled_data['verified_cooperatives']:
        if c.get('source') == 'iowa_sos':
            new_cats[c['category']] += 1

    print("\nIowa SoS cooperatives by category:")
    for cat, count in new_cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()

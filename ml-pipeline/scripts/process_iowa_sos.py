#!/usr/bin/env python3
"""
Process Iowa Secretary of State business entity data to find cooperatives.

Source: https://data.iowa.gov/Regulation/Active-Iowa-Business-Entities/ez5t-3qay
"""

import csv
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SOS_FILE = DATA_DIR / "iowa_business_entities.csv"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"
CANDIDATES_FILE = DATA_DIR / "candidates.json"
OUTPUT_FILE = DATA_DIR / "sos_candidates.json"

# Corporation types that are explicitly cooperatives
COOP_CORP_TYPES = [
    "CO-OP NON STOCK",
    "CO-OP STOCK",
    "DOMESTIC COOPERATIVE",
    "CO-OP STOCK VALUE ADDED",
]

# Keywords in business names that suggest cooperatives
COOP_KEYWORDS = [
    "cooperative",
    "co-operative",
    "co-op",
    "coop",
    "credit union",
    "rural electric",
    "power cooperative",
    "telephone cooperative",
    "telecom cooperative",
]

# Exclude these patterns (not the cooperatives we're looking for)
EXCLUDE_PATTERNS = [
    r"housing",
    r"residential",
    r"homeowners",
    r"apartment",
    r"condo",
    r"hoa",
    r"vintage cooperative community",  # These are retirement communities
    r"homestead cooperative",
    r"co-op,?\s*inc\.?$",  # Generic "X CO-OP, INC." are usually housing
    r"^\d+.*co-?op",  # Address-named co-ops like "721 WILSON COOPERATIVE"
    r"street.*co-?op",  # Street-named co-ops
    r"avenue.*co-?op",
    r"drive.*co-?op",
    r"place.*co-?op",
    r"turtle cove",
    r"blue sky",
    r"properties cooperative",
]

# Corporation types to EXCLUDE (housing-related)
EXCLUDE_CORP_TYPES = [
    "MULTIPLE HOUSING ACT",
]


def normalize_name(name: str) -> str:
    """Normalize name for comparison."""
    name = name.lower().strip()
    name = re.sub(r'["\',.]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name


def is_excluded(name: str) -> bool:
    """Check if name matches exclusion patterns."""
    name_lower = name.lower()
    return any(re.search(pat, name_lower) for pat in EXCLUDE_PATTERNS)


def get_verified_names(labeled_data):
    """Get set of normalized names from verified cooperatives."""
    names = set()
    for coop in labeled_data['verified_cooperatives']:
        names.add(normalize_name(coop['name']))
    return names


def get_existing_candidate_names(candidates):
    """Get set of normalized names from existing candidates."""
    names = set()
    for c in candidates:
        names.add(normalize_name(c['name']))
    return names


def extract_city_from_address(row):
    """Extract city from Home Office or Registered Agent address."""
    # Try Home Office city first
    city = row.get('HO City', '').strip()
    if city:
        return city
    # Fall back to Registered Agent city
    city = row.get('RA City', '').strip()
    return city if city else "Iowa"


def process_sos_data():
    """Process Iowa SoS data and extract cooperatives."""

    print("Loading labeled data and existing candidates...")
    with open(LABELED_DATA_PATH) as f:
        labeled_data = json.load(f)

    with open(CANDIDATES_FILE) as f:
        existing_candidates = json.load(f)

    verified_names = get_verified_names(labeled_data)
    existing_names = get_existing_candidate_names(existing_candidates)

    print(f"  Verified cooperatives: {len(verified_names)}")
    print(f"  Existing candidates: {len(existing_names)}")

    print(f"\nProcessing {SOS_FILE}...")

    candidates = []
    stats = {
        'total_rows': 0,
        'coop_by_type': 0,
        'coop_by_name': 0,
        'excluded': 0,
        'already_verified': 0,
        'already_candidate': 0,
        'new_candidates': 0,
    }

    with open(SOS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            stats['total_rows'] += 1

            name = row.get('Legal Name', '').strip()
            corp_type = row.get('Corporation Type', '').strip()

            if not name:
                continue

            # Skip excluded corporation types (like housing)
            if corp_type in EXCLUDE_CORP_TYPES:
                continue

            # Check if it's a cooperative by corporation type
            is_coop_type = corp_type in COOP_CORP_TYPES

            # Check if it's a cooperative by name keywords
            name_lower = name.lower()
            is_coop_name = any(kw in name_lower for kw in COOP_KEYWORDS)

            if not (is_coop_type or is_coop_name):
                continue

            if is_coop_type:
                stats['coop_by_type'] += 1
            if is_coop_name:
                stats['coop_by_name'] += 1

            # Check exclusions
            if is_excluded(name):
                stats['excluded'] += 1
                continue

            # Check if already verified
            norm_name = normalize_name(name)
            if norm_name in verified_names:
                stats['already_verified'] += 1
                continue

            # Check if already a candidate
            if norm_name in existing_names:
                stats['already_candidate'] += 1
                continue

            # Extract location
            city = extract_city_from_address(row)
            location = f"{city}, IA" if city != "Iowa" else "Iowa"

            # Determine category based on name
            category = 'other'
            if 'electric' in name_lower or 'power' in name_lower:
                category = 'electric'
            elif 'telephone' in name_lower or 'telecom' in name_lower:
                category = 'telecom'
            elif 'credit union' in name_lower:
                category = 'credit'
            elif any(kw in name_lower for kw in ['farm', 'grain', 'elevator', 'seed', 'agri', 'dairy']):
                category = 'agricultural'
            elif 'food' in name_lower or 'market' in name_lower or 'grocery' in name_lower:
                category = 'food'

            candidate = {
                'name': name,
                'website': None,
                'location': location,
                'source': 'iowa_sos',
                'corp_type': corp_type,
                'corp_number': row.get('Corp Number', ''),
                'category_hint': category,
                'needs_website': True,
            }

            candidates.append(candidate)
            existing_names.add(norm_name)  # Prevent duplicates within this run
            stats['new_candidates'] += 1

    # Save SoS-specific candidates
    print(f"\nSaving {len(candidates)} new candidates to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(candidates, f, indent=2)

    # Print stats
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Total rows processed: {stats['total_rows']:,}")
    print(f"Cooperatives by corp type: {stats['coop_by_type']}")
    print(f"Cooperatives by name keyword: {stats['coop_by_name']}")
    print(f"Excluded (housing/residential): {stats['excluded']}")
    print(f"Already verified: {stats['already_verified']}")
    print(f"Already in candidates: {stats['already_candidate']}")
    print(f"NEW candidates found: {stats['new_candidates']}")

    # Category breakdown
    print("\nNew candidates by category hint:")
    from collections import Counter
    cat_counts = Counter(c['category_hint'] for c in candidates)
    for cat, count in cat_counts.most_common():
        print(f"  {cat}: {count}")

    print("\n" + "="*60)
    print("SAMPLE NEW CANDIDATES")
    print("="*60)
    for c in candidates[:15]:
        print(f"  {c['name'][:50]:<50} ({c['category_hint']})")

    return candidates


if __name__ == "__main__":
    process_sos_data()

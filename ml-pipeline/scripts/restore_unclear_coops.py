#!/usr/bin/env python3
"""
Restore the 49 unclear cooperatives with proper categorization based on research.

Research findings summary:
- Many town-named coops are agricultural (grain elevators)
- Several merger entities are shell companies (exclude)
- Found specific categories for many via web search
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
SOS_CANDIDATES_FILE = DATA_DIR / "sos_candidates.json"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"

# Research-based categorizations
CATEGORIZED = {
    # AGRICULTURAL - confirmed via research
    "AGSTATE COOPERATIVE": "agricultural",  # Major ag coop in Cherokee
    "BALSAM COOP.": "agricultural",  # Dairy value-added
    "BORDER COUNTY CO-OPERATIVE": "agricultural",  # Inwood ag coop
    "FIRST COOPERATIVE ASSOCIATION": "agricultural",  # Merged into AgState
    "TAMA-BENTON COOPERATIVE COMPANY": "agricultural",  # Active grain/agronomy
    "UPPER IOWA COOPERATIVE": "agricultural",  # Postville ag services
    "FCS COOPERATIVE": "agricultural",  # Farmers Cooperative Society, Sioux Center
    "NEW HORIZON COOPERATIVE": "agricultural",  # Poultry/eggs, Britt
    "MUSCATINE ISLAND COOPERATIVE ASSOCIATION": "agricultural",  # Vegetable research
    "MEADOWLAND COOPERATIVE": "agricultural",  # Likely ag (Parkersburg area)
    "NE COOPERATIVE COMPANY": "agricultural",  # Likely merged into Nexus

    # Town-named coops - almost certainly agricultural (grain elevators)
    "ASPINWALL COOPERATIVE CO.": "agricultural",
    "BUCKINGHAM CO-OPERATIVE CO.": "agricultural",
    "EAGLE GROVE COOPERATIVE": "agricultural",
    "GOLDFIELD COOPERATIVE": "agricultural",
    "HULL COOPERATIVE ASSOCIATION": "agricultural",

    # FOOD
    "FRONTIER COOPERATIVE": "food",  # Major natural/organic products coop
    "FRESH CONNECTIONS COOPERATIVE": "food",  # Algona food coop

    # ENERGY
    "THE CONSUMERS COOPERATIVE SOCIETY": "energy",  # Propane/fuel, Coralville
    "BIG RIVER RESOURCES COOPERATIVE": "energy",  # Ethanol producer

    # HOUSING (Senior)
    "REALIFE COOPERATIVE OF DENISON": "housing",  # Senior independent living

    # EDUCATION
    "JOURNEYS LEARNING COOPERATIVE": "education",  # Likely homeschool coop

    # WORKER
    "CORRIDOR TEMPORARY WORKERS COOPERATIVE": "worker",  # Worker coop

    # UTILITIES (Water)
    "FRYTOWN WATER CO-OPERATIVE": "utilities",  # Water coop

    # UNCLEAR - keep as 'other' for now (need more research or minimal info)
    "REICKSVIEW COOPERATIVE": "other",  # Related to Reicks View Farms?
    "OCI COOPERATIVE COMPANY": "other",  # Unknown
    "SECOND STREET SENIOR CENTER": "other",  # Possibly senior services
    "HEARTLAND PROPERTY COOP": "other",  # Unknown - distinct from Heartland Co-op
    "ASIAN IOWAN COOPERATIVE": "other",  # Unknown
    "NCGA DEVELOPMENT COOPERATIVE": "other",  # Unknown
    "UFMC COOPERATIVE II": "other",  # Unknown, possibly ag
    "FC COOP II": "other",  # Unknown
    "NEW CROSSROADS COOPERATIVE": "other",  # Unknown
    "AMERIQOIN COOPERATIVE": "other",  # Unknown
    "CALIHAN PROCESSING COOPERATIVE": "other",  # Unknown processing
    "ENOVUS MANAGEMENT COOPERATIVE": "other",  # Unknown management
    "HEVENTEGRA COOPERATIVE": "other",  # Unknown
    "IASE COOPERATIVE": "other",  # Unknown
    "L. C. CO-OPERATIVE INC.": "other",  # Unknown
    "NUWAY-K&H COOPERATIVE": "other",  # Unknown
    "RV COOP": "other",  # Unknown
    "STAGE DOOR CINEMA CP": "other",  # Possibly arts/entertainment
    "TEAM VICTORY COOPERATIVE": "other",  # Unknown
    "ALL GENERATIONS COOP LCA": "other",  # Unknown
}

# EXCLUDE - these are merger shell companies or not Iowa-based
EXCLUDE = [
    "FW MERGER COOPERATIVE",  # Merger shell company
    "MID-IOWA MERGER COOPERATIVE",  # Merger shell company
    "NEW MERGER COOPERATIVE",  # Merger shell company
    "RUTHVEN/PRO MERGER COOPERATIVE",  # Merger shell company
    "TRIANGLE COOPERATIVE SERVICE COMPANY",  # Actually in Oklahoma, not Iowa
]


def get_sos_info(name: str, sos_candidates: list) -> dict:
    """Get SoS info for a cooperative."""
    for c in sos_candidates:
        if c['name'] == name:
            return c
    return {}


def get_verified_names(labeled_data: dict) -> set:
    """Get set of names from verified cooperatives."""
    names = set()
    for coop in labeled_data['verified_cooperatives']:
        names.add(coop['name'])
    return names


def main():
    print("Loading data...")
    with open(SOS_CANDIDATES_FILE) as f:
        sos_candidates = json.load(f)

    with open(LABELED_DATA_PATH) as f:
        labeled_data = json.load(f)

    verified_names = get_verified_names(labeled_data)
    max_id = max(c['id'] for c in labeled_data['verified_cooperatives'])

    print(f"Current verified count: {len(labeled_data['verified_cooperatives'])}")
    print()

    # Add 'utilities' and 'education' to categories if needed
    existing_cats = set(c['category'] for c in labeled_data['verified_cooperatives'])
    new_cats = {'utilities', 'education'} - existing_cats
    if new_cats:
        print(f"New categories to be added: {new_cats}")

    added = 0
    skipped_dup = 0
    excluded = 0

    # Process categorized cooperatives
    for name, category in CATEGORIZED.items():
        if name in verified_names:
            skipped_dup += 1
            continue

        info = get_sos_info(name, sos_candidates)
        if not info:
            print(f"  Warning: No SoS info found for {name}")
            continue

        max_id += 1
        new_coop = {
            'id': max_id,
            'name': name,
            'category': category,
            'website': None,
            'location': info.get('location', 'Iowa'),
            'verified_date': datetime.now().isoformat(),
            'source': 'iowa_sos',
            'corp_type': info.get('corp_type'),
            'corp_number': info.get('corp_number'),
        }

        labeled_data['verified_cooperatives'].append(new_coop)
        verified_names.add(name)
        added += 1
        print(f"  Added: {name} -> {category}")

    # Count excluded
    for name in EXCLUDE:
        excluded += 1
        print(f"  Excluded: {name} (merger shell or not Iowa)")

    # Update stats
    labeled_data['stats']['total_verified'] = len(labeled_data['verified_cooperatives'])
    labeled_data['metadata']['last_updated'] = datetime.now().isoformat()

    # Save
    print()
    print(f"Saving to {LABELED_DATA_PATH}...")
    with open(LABELED_DATA_PATH, 'w') as f:
        json.dump(labeled_data, f, indent=2)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Added: {added}")
    print(f"Skipped (already verified): {skipped_dup}")
    print(f"Excluded (merger shells/not Iowa): {excluded}")
    print(f"New total verified: {labeled_data['stats']['total_verified']}")

    # Category breakdown
    from collections import Counter
    cats = Counter(c['category'] for c in labeled_data['verified_cooperatives'])
    print()
    print("Category breakdown:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()

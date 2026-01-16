#!/usr/bin/env python3
"""
Investigate unclear cooperatives from Iowa SoS data.

This script finds cooperatives that were marked as unclear/other and helps
investigate them one by one to determine proper categorization.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
SOS_CANDIDATES_FILE = DATA_DIR / "sos_candidates.json"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"

# The 49 cooperatives that were removed and need investigation
UNCLEAR_COOPS = [
    "AGSTATE COOPERATIVE",
    "ALL GENERATIONS COOP LCA",
    "AMERIQOIN COOPERATIVE",
    "ASIAN IOWAN COOPERATIVE",
    "ASPINWALL COOPERATIVE CO.",
    "BALSAM COOP.",
    "BIG RIVER RESOURCES COOPERATIVE",
    "BORDER COUNTY CO-OPERATIVE",
    "BUCKINGHAM CO-OPERATIVE CO.",
    "CALIHAN PROCESSING COOPERATIVE",
    "CORRIDOR TEMPORARY WORKERS COOPERATIVE",
    "EAGLE GROVE COOPERATIVE",
    "ENOVUS MANAGEMENT COOPERATIVE",
    "FC COOP II",
    "FCS COOPERATIVE",
    "FIRST COOPERATIVE ASSOCIATION",
    "FRESH CONNECTIONS COOPERATIVE",
    "FRONTIER COOPERATIVE",
    "FRYTOWN WATER CO-OPERATIVE",
    "FW MERGER COOPERATIVE",
    "GOLDFIELD COOPERATIVE",
    "HEARTLAND PROPERTY COOP",
    "HEVENTEGRA COOPERATIVE",
    "HULL COOPERATIVE ASSOCIATION",
    "IASE COOPERATIVE",
    "JOURNEYS LEARNING COOPERATIVE",
    "L. C. CO-OPERATIVE INC.",
    "MEADOWLAND COOPERATIVE",
    "MID-IOWA MERGER COOPERATIVE",
    "MUSCATINE ISLAND COOPERATIVE ASSOCIATION",
    "NCGA DEVELOPMENT COOPERATIVE",
    "NE COOPERATIVE COMPANY",
    "NEW CROSSROADS COOPERATIVE",
    "NEW HORIZON COOPERATIVE",
    "NEW MERGER COOPERATIVE",
    "NUWAY-K&H COOPERATIVE",
    "OCI COOPERATIVE COMPANY",
    "REALIFE COOPERATIVE OF DENISON",
    "REICKSVIEW COOPERATIVE",
    "RUTHVEN/PRO MERGER COOPERATIVE",
    "RV COOP",
    "SECOND STREET SENIOR CENTER",
    "STAGE DOOR CINEMA CP",
    "TAMA-BENTON COOPERATIVE COMPANY",
    "TEAM VICTORY COOPERATIVE",
    "THE CONSUMERS COOPERATIVE SOCIETY",
    "TRIANGLE COOPERATIVE SERVICE COMPANY",
    "UFMC COOPERATIVE II",
    "UPPER IOWA COOPERATIVE",
]


def get_sos_info(name: str, sos_candidates: list) -> dict:
    """Get SoS info for a cooperative."""
    for c in sos_candidates:
        if c['name'] == name:
            return c
    return {}


def get_verified_names(labeled_data: dict) -> set:
    """Get set of normalized names from verified cooperatives."""
    names = set()
    for coop in labeled_data['verified_cooperatives']:
        names.add(coop['name'].lower().strip())
    return names


def restore_coops():
    """Restore the removed cooperatives and show their info for investigation."""

    print("Loading data...")
    with open(SOS_CANDIDATES_FILE) as f:
        sos_candidates = json.load(f)

    with open(LABELED_DATA_PATH) as f:
        labeled_data = json.load(f)

    verified_names = get_verified_names(labeled_data)
    max_id = max(c['id'] for c in labeled_data['verified_cooperatives'])

    print(f"Current verified count: {len(labeled_data['verified_cooperatives'])}")
    print(f"Unclear coops to investigate: {len(UNCLEAR_COOPS)}")
    print()

    # Check which ones are missing from verified list
    missing = []
    for name in UNCLEAR_COOPS:
        if name.lower().strip() not in verified_names:
            info = get_sos_info(name, sos_candidates)
            missing.append((name, info))

    print(f"Missing from verified (need restoration): {len(missing)}")
    print()
    print("=" * 80)
    print("COOPERATIVES TO INVESTIGATE")
    print("=" * 80)
    print()

    for i, (name, info) in enumerate(missing, 1):
        print(f"{i:2}. {name}")
        if info:
            print(f"    Location: {info.get('location', 'Unknown')}")
            print(f"    Corp Type: {info.get('corp_type', 'Unknown')}")
            print(f"    Category Hint: {info.get('category_hint', 'other')}")
        print()


def show_investigation_details():
    """Show detailed info for investigation."""

    print("Loading SoS candidates...")
    with open(SOS_CANDIDATES_FILE) as f:
        sos_candidates = json.load(f)

    print()
    print("=" * 80)
    print("DETAILED INVESTIGATION INFO")
    print("=" * 80)
    print()

    # Group by patterns
    town_named = []  # Likely agricultural - named after towns
    merger = []      # Merger shell companies - may exclude
    worker = []      # Worker cooperatives
    water = []       # Water cooperatives
    resources = []   # Resource/ethanol cooperatives
    other = []       # Need web research

    for name in UNCLEAR_COOPS:
        info = get_sos_info(name, sos_candidates)
        name_lower = name.lower()

        # Check patterns
        if 'merger' in name_lower:
            merger.append((name, info))
        elif 'water' in name_lower:
            water.append((name, info))
        elif 'worker' in name_lower or 'temporary' in name_lower:
            worker.append((name, info))
        elif 'resources' in name_lower or 'ethanol' in name_lower:
            resources.append((name, info))
        elif any(town in name_lower for town in ['aspinwall', 'buckingham', 'eagle grove', 'goldfield', 'hull']):
            town_named.append((name, info))
        else:
            other.append((name, info))

    def print_group(title, items, suggested_cat):
        if not items:
            return
        print(f"\n### {title} (suggested: {suggested_cat})")
        print("-" * 60)
        for name, info in items:
            loc = info.get('location', 'Unknown') if info else 'Unknown'
            corp = info.get('corp_type', 'Unknown') if info else 'Unknown'
            print(f"  - {name}")
            print(f"    Location: {loc}, Corp Type: {corp}")

    print_group("TOWN-NAMED CO-OPS", town_named, "agricultural")
    print_group("MERGER ENTITIES", merger, "EXCLUDE - shell companies")
    print_group("WORKER CO-OPS", worker, "worker")
    print_group("WATER CO-OPS", water, "utilities")
    print_group("RESOURCE/ETHANOL CO-OPS", resources, "energy")
    print_group("NEED RESEARCH", other, "various - need web lookup")

    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Town-named (likely agricultural): {len(town_named)}")
    print(f"Merger entities (likely exclude): {len(merger)}")
    print(f"Worker cooperatives: {len(worker)}")
    print(f"Water cooperatives: {len(water)}")
    print(f"Resource/ethanol: {len(resources)}")
    print(f"Need research: {len(other)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--details":
        show_investigation_details()
    else:
        restore_coops()
        print("\nRun with --details for categorization suggestions")

#!/usr/bin/env python3
"""
Fetch candidate cooperatives from multiple authoritative sources.

Sources:
1. NCUA credit union data (Iowa credit unions)
2. Iowa Association of Electric Cooperatives member list
3. Web search for additional Iowa cooperatives

This script generates a comprehensive candidates.json file.
"""

import json
import csv
import re
from pathlib import Path
from urllib.parse import urlparse

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"
CANDIDATES_FILE = DATA_DIR / "candidates.json"
NCUA_FILE = DATA_DIR / "FOICU.txt"


def load_labeled_data():
    """Load labeled data to check for existing cooperatives."""
    with open(LABELED_DATA_PATH) as f:
        return json.load(f)


def normalize_name(name: str) -> str:
    """Normalize business name for comparison."""
    name = name.lower().strip()
    # Remove common suffixes
    for suffix in [", inc", " inc", ", llc", " llc", ", ltd", " ltd", "."]:
        name = name.replace(suffix, "")
    # Remove extra whitespace
    name = " ".join(name.split())
    return name


def extract_domain(url: str) -> str | None:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return None


def get_verified_identifiers(labeled_data):
    """Get set of names and domains already verified."""
    identifiers = set()
    for coop in labeled_data['verified_cooperatives']:
        identifiers.add(normalize_name(coop['name']))
        if coop.get('website'):
            domain = extract_domain(coop['website'])
            if domain:
                identifiers.add(domain)
    return identifiers


def fetch_ncua_credit_unions():
    """Extract Iowa credit unions from NCUA data file."""
    candidates = []

    if not NCUA_FILE.exists():
        print("  NCUA file not found. Run: curl -L -o ncua_data.zip 'https://ncua.gov/files/publications/analysis/call-report-data-2024-12.zip' && unzip ncua_data.zip")
        return candidates

    with open(NCUA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filter for Iowa (CharterState or STATE = IA)
            if row.get('STATE') == 'IA' or row.get('CharterState') == 'IA':
                name = row.get('CU_NAME', '').strip()
                city = row.get('CITY', '').strip()

                # Skip if name is empty
                if not name:
                    continue

                # Clean up name - add "Credit Union" if not present
                if 'credit union' not in name.lower() and 'cu' not in name.lower():
                    display_name = f"{name} Credit Union"
                else:
                    display_name = name

                candidates.append({
                    'name': display_name,
                    'website': None,  # NCUA data doesn't include websites
                    'location': f"{city}, IA" if city else "Iowa",
                    'source': 'ncua',
                    'ncua_number': row.get('CU_NUMBER'),
                    'needs_website': True
                })

    return candidates


def get_iaec_electric_coops():
    """
    Iowa Association of Electric Cooperatives members.
    Source: https://www.iowarec.org/iowa-co-ops/our-members
    """
    # Data extracted from IAEC website
    coops = [
        {"name": "Access Energy Cooperative", "website": "https://www.accessenergycoop.com/", "location": "Mt. Pleasant, IA"},
        {"name": "Allamakee-Clayton Electric Cooperative", "website": "https://www.acrec.com/", "location": "Postville, IA"},
        {"name": "Boone Valley Electric Cooperative", "website": "https://www.cbpower.coop/", "location": "Renwick, IA"},
        {"name": "Butler County Rural Electric Cooperative", "website": "https://www.butlerrec.coop/", "location": "Allison, IA"},
        {"name": "Calhoun County Electric Cooperative Association", "website": "https://www.calhounrec.coop/", "location": "Rockwell City, IA"},
        {"name": "Chariton Valley Electric Cooperative", "website": "https://www.cvrec.com/", "location": "Albia, IA"},
        {"name": "Clarke Electric Cooperative", "website": "https://www.cecnet.net/", "location": "Osceola, IA"},
        {"name": "Consumers Energy Cooperative", "website": "https://www.consumersenergy.coop/", "location": "Marshalltown, IA"},
        {"name": "Corridor Energy Cooperative", "website": "https://www.corridorenergy.coop/", "location": "Boone, IA"},
        {"name": "East-Central Iowa Rural Electric Cooperative", "website": "https://www.ecirec.coop/", "location": "Urbana, IA"},
        {"name": "Eastern Iowa Light & Power Cooperative", "website": "https://www.easterniowa.com/", "location": "Wilton, IA"},
        {"name": "Farmers Electric Cooperative (Greenfield)", "website": "https://www.farmersrec.com/", "location": "Greenfield, IA"},
        {"name": "Franklin Rural Electric Cooperative", "website": "https://www.franklinrec.coop/", "location": "Hampton, IA"},
        {"name": "Grundy County Rural Electric Cooperative", "website": "https://www.grundycountyrecia.com/", "location": "Grundy Center, IA"},
        {"name": "Guthrie County Rural Electric Cooperative", "website": "https://www.guthrie-rec.coop/", "location": "Guthrie Center, IA"},
        {"name": "Harrison County Rural Electric Cooperative", "website": "https://www.hcrec.coop/", "location": "Woodbine, IA"},
        {"name": "Heartland Power Cooperative", "website": "https://www.heartlandpower.com/", "location": "Thompson, IA"},
        {"name": "Iowa Lakes Electric Cooperative", "website": "https://www.ilec.coop/", "location": "Estherville, IA"},
        {"name": "L&O Power Cooperative", "website": "https://www.landopowercoop.com/", "location": "Rock Rapids, IA"},
        {"name": "Lyon Rural Electric Cooperative", "website": "https://www.lyonrec.coop/", "location": "Rock Rapids, IA"},
        {"name": "Maquoketa Valley Electric Cooperative", "website": "https://www.mvec.coop/", "location": "Anamosa, IA"},
        {"name": "Midland Power Cooperative", "website": "https://www.midlandpower.coop/", "location": "Jefferson, IA"},
        {"name": "MiEnergy Cooperative", "website": "https://www.mienergy.coop/", "location": "Cresco, IA"},
        {"name": "Nishnabotna Valley Rural Electric Cooperative", "website": "https://www.nvrec.com/", "location": "Harlan, IA"},
        {"name": "North West Rural Electric Cooperative", "website": "https://www.nwrec.com/", "location": "Orange City, IA"},
        {"name": "Northwest Iowa Power Cooperative (NIPCO)", "website": "https://www.nipco.coop/", "location": "Le Mars, IA"},
        {"name": "Osceola Electric Cooperative", "website": "https://www.osceolaelectric.com/", "location": "Sibley, IA"},
        {"name": "Pella Cooperative Electric Association", "website": "https://www.pella-cea.org/", "location": "Pella, IA"},
        {"name": "Prairie Energy Cooperative", "website": "https://www.prairieenergy.coop/", "location": "Clarion, IA"},
        {"name": "Raccoon Valley Electric Cooperative", "website": "https://www.rvec.coop/", "location": "Glidden, IA"},
        {"name": "Southern Iowa Electric Cooperative", "website": "https://www.sie.coop/", "location": "Bloomfield, IA"},
        {"name": "Southwest Iowa Rural Electric Cooperative", "website": "https://www.swiarec.coop/", "location": "Corning, IA"},
        {"name": "T.I.P. Rural Electric Cooperative", "website": "https://www.tiprec.com/", "location": "Brooklyn, IA"},
        {"name": "Western Iowa Power Cooperative (WIPCO)", "website": "https://www.wipco.com/", "location": "Denison, IA"},
        {"name": "Woodbury County Rural Electric Cooperative", "website": "https://www.woodburyrec.com/", "location": "Moville, IA"},
        # Generation & Transmission Cooperatives
        {"name": "Central Iowa Power Cooperative (CIPCO)", "website": "https://www.cipco.net/", "location": "Cedar Rapids, IA"},
        {"name": "Corn Belt Power Cooperative", "website": "https://www.cbpower.coop/", "location": "Humboldt, IA"},
    ]

    candidates = []
    for coop in coops:
        candidates.append({
            'name': coop['name'],
            'website': coop['website'],
            'location': coop['location'],
            'source': 'iaec'
        })

    return candidates


def search_additional_cooperatives():
    """
    Additional known Iowa cooperatives from various sources.
    """
    coops = [
        # Agricultural Cooperatives
        {"name": "Ag Partners Cooperative", "website": "https://www.agpartnerscoop.com/", "location": "Iowa", "source": "web_search"},
        {"name": "Hawkeye Cooperative", "website": "https://www.hawkeyecooperative.com/", "location": "Iowa", "source": "web_search"},
        {"name": "Farmers Cooperative Association Stratford", "website": "https://www.stratfordcoop.com/", "location": "Stratford, IA", "source": "web_search"},
        {"name": "Frontier Cooperative", "website": "https://www.frontiercoop.com/", "location": "Nebraska/Iowa", "source": "web_search"},
        {"name": "Landus Cooperative", "website": "https://www.landus.coop/", "location": "Ames, IA", "source": "web_search"},
        {"name": "Key Cooperative", "website": "https://www.keycooperative.com/", "location": "Roland, IA", "source": "web_search"},
        {"name": "NEW Cooperative", "website": "https://www.newcoop.com/", "location": "Fort Dodge, IA", "source": "web_search"},
        {"name": "United Farmers Cooperative", "website": "https://www.ufcgrainco.com/", "location": "Alden, IA", "source": "web_search"},
        {"name": "Farmers Cooperative Company", "website": "https://www.farmerscooperative.com/", "location": "Farnhamville, IA", "source": "web_search"},
        {"name": "West Central Cooperative", "website": "https://www.westcentral.coop/", "location": "Ralston, IA", "source": "web_search"},
        {"name": "North Central Cooperative", "website": "https://www.northcentralcoop.com/", "location": "Manly, IA", "source": "web_search"},
        {"name": "Innovative Ag Services", "website": "https://www.ikiowa.com/", "location": "Monticello, IA", "source": "web_search"},
        {"name": "Premier Cooperative", "website": "https://www.premiercooperative.com/", "location": "Reinbeck, IA", "source": "web_search"},
        {"name": "Stateline Cooperative", "website": "https://www.statelinecoop.com/", "location": "Larchwood, IA", "source": "web_search"},

        # Credit Unions (with known websites)
        {"name": "Veridian Credit Union", "website": "https://www.veridiancu.org/", "location": "Waterloo, IA", "source": "web_search"},
        {"name": "Collins Community Credit Union", "website": "https://www.collinscu.org/", "location": "Cedar Rapids, IA", "source": "web_search"},
        {"name": "DuPont Community Credit Union", "website": "https://www.dupontccu.org/", "location": "Fort Madison, IA", "source": "web_search"},
        {"name": "Ascentra Credit Union", "website": "https://www.ascentra.org/", "location": "Davenport, IA", "source": "web_search"},
        {"name": "GreenState Credit Union", "website": "https://www.greenstate.org/", "location": "North Liberty, IA", "source": "web_search"},
        {"name": "Community Choice Credit Union", "website": "https://www.communitychoicecu.com/", "location": "Johnston, IA", "source": "web_search"},

        # Telecom Cooperatives
        {"name": "Farmers Mutual Telephone Company", "website": "https://www.fmtc.coop/", "location": "Bellingham, IA", "source": "web_search"},
        {"name": "Winnebago Cooperative Telecom Association", "website": "https://www.wctatel.net/", "location": "Lake Mills, IA", "source": "web_search"},
        {"name": "Coon Valley Telecommunications Cooperative", "website": "https://www.coonvalleytelco.com/", "location": "Manning, IA", "source": "web_search"},
        {"name": "Northeast Iowa Telephone Company", "website": "https://www.neitel.com/", "location": "Monona, IA", "source": "web_search"},
        {"name": "Mahaska Communication Group", "website": "https://www.mahaska.org/", "location": "Oskaloosa, IA", "source": "web_search"},

        # Food Cooperatives
        {"name": "New Pioneer Food Co-op", "website": "https://www.newpi.coop/", "location": "Iowa City, IA", "source": "web_search"},
        {"name": "Wheatsfield Cooperative", "website": "https://www.wheatsfield.coop/", "location": "Ames, IA", "source": "web_search"},
        {"name": "Oneota Community Food Co-op", "website": "https://www.oneotacoop.com/", "location": "Decorah, IA", "source": "web_search"},

        # Housing Cooperatives
        {"name": "River Hills Cooperative", "website": "https://www.riverhillscoop.org/", "location": "Des Moines, IA", "source": "web_search"},
    ]

    return coops


def deduplicate_candidates(candidates, verified_identifiers):
    """Remove candidates that are already verified."""
    deduped = []
    seen = set()

    for c in candidates:
        name_norm = normalize_name(c['name'])
        domain = extract_domain(c.get('website', '')) if c.get('website') else None

        # Skip if already verified
        if name_norm in verified_identifiers:
            print(f"  Skipping (verified): {c['name']}")
            continue
        if domain and domain in verified_identifiers:
            print(f"  Skipping (domain match): {c['name']}")
            continue

        # Skip duplicates within candidates
        key = name_norm
        if key in seen:
            continue
        seen.add(key)

        deduped.append(c)

    return deduped


def main():
    print("=" * 60)
    print("FETCHING COOPERATIVE CANDIDATES")
    print("=" * 60)

    # Load labeled data for deduplication
    print("\nLoading labeled data...")
    labeled_data = load_labeled_data()
    verified_ids = get_verified_identifiers(labeled_data)
    print(f"Found {len(labeled_data['verified_cooperatives'])} verified cooperatives")

    all_candidates = []

    # 1. NCUA Credit Unions
    print("\n" + "-" * 40)
    print("Fetching NCUA Iowa Credit Unions...")
    ncua_candidates = fetch_ncua_credit_unions()
    print(f"Found {len(ncua_candidates)} Iowa credit unions")
    all_candidates.extend(ncua_candidates)

    # 2. IAEC Electric Cooperatives
    print("\n" + "-" * 40)
    print("Fetching IAEC Electric Cooperatives...")
    iaec_candidates = get_iaec_electric_coops()
    print(f"Found {len(iaec_candidates)} electric cooperatives")
    all_candidates.extend(iaec_candidates)

    # 3. Additional web search cooperatives
    print("\n" + "-" * 40)
    print("Adding additional known cooperatives...")
    additional = search_additional_cooperatives()
    print(f"Found {len(additional)} additional cooperatives")
    all_candidates.extend(additional)

    # Deduplicate
    print("\n" + "-" * 40)
    print("Deduplicating candidates...")
    candidates = deduplicate_candidates(all_candidates, verified_ids)
    print(f"After deduplication: {len(candidates)} candidates")

    # Separate by whether they have websites
    with_websites = [c for c in candidates if c.get('website') and not c.get('needs_website')]
    needs_websites = [c for c in candidates if c.get('needs_website') or not c.get('website')]

    print(f"\n  With websites (ready for ML): {len(with_websites)}")
    print(f"  Need website lookup: {len(needs_websites)}")

    # Save candidates
    print(f"\nSaving to {CANDIDATES_FILE}")
    with open(CANDIDATES_FILE, 'w') as f:
        json.dump(candidates, f, indent=2)

    # Also save a separate file for candidates that need website lookup
    needs_website_file = DATA_DIR / "candidates_need_websites.json"
    with open(needs_website_file, 'w') as f:
        json.dump(needs_websites, f, indent=2)
    print(f"Saved candidates needing websites to {needs_website_file}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total candidates: {len(candidates)}")
    print(f"  - NCUA credit unions: {len([c for c in candidates if c.get('source') == 'ncua'])}")
    print(f"  - IAEC electric coops: {len([c for c in candidates if c.get('source') == 'iaec'])}")
    print(f"  - Other sources: {len([c for c in candidates if c.get('source') not in ['ncua', 'iaec']])}")
    print("\nNEXT STEPS:")
    print("1. Look up websites for candidates in candidates_need_websites.json")
    print("2. Run: python scripts/scrape_websites.py (to extract content)")
    print("3. Run: python scripts/similarity_search.py (to score candidates)")
    print("=" * 60)


if __name__ == "__main__":
    main()

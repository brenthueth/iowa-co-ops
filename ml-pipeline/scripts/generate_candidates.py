#!/usr/bin/env python3
"""
Generate candidate cooperatives from various sources.

Data sources:
1. Iowa Secretary of State business search (manual export needed)
2. Web search for Iowa cooperatives
3. Known cooperative directories

This script provides utilities to process and deduplicate candidates.
"""

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
VERIFIED_FILE = DATA_DIR / "verified_cooperatives.json"
CANDIDATES_FILE = DATA_DIR / "candidates.json"

# Keywords that suggest a cooperative
COOP_KEYWORDS = [
    "cooperative", "co-operative", "co-op", "coop",
    "credit union", "federal credit union",
    "rural electric", "rec", "reca",
    "mutual", "farmers",
]

# Iowa cities for filtering
IOWA_INDICATORS = [
    ", ia", ", iowa", "iowa"
]


def load_verified_cooperatives() -> set:
    """Load names of already verified cooperatives."""
    with open(VERIFIED_FILE) as f:
        coops = json.load(f)

    # Create set of normalized names for deduplication
    names = set()
    for c in coops:
        names.add(normalize_name(c["name"]))
        # Also add website domain
        if c.get("website"):
            domain = extract_domain(c["website"])
            if domain:
                names.add(domain)

    return names


def normalize_name(name: str) -> str:
    """Normalize business name for comparison."""
    name = name.lower()
    # Remove common suffixes
    for suffix in [", inc", " inc", ", llc", " llc", ", ltd", " ltd", "."]:
        name = name.replace(suffix, "")
    # Remove extra whitespace
    name = " ".join(name.split())
    return name


def extract_domain(url: str) -> str | None:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return None


def is_likely_cooperative(name: str, description: str = "") -> bool:
    """Check if a business name/description suggests it's a cooperative."""
    text = f"{name} {description}".lower()
    return any(kw in text for kw in COOP_KEYWORDS)


def is_iowa_business(location: str) -> bool:
    """Check if location indicates Iowa."""
    location = location.lower()
    return any(ind in location for ind in IOWA_INDICATORS)


def search_usda_cooperatives():
    """
    Search USDA cooperative directory.
    Note: This would require API access or scraping their database.
    Returns placeholder for manual data entry.
    """
    print("USDA Cooperative Directory:")
    print("  Visit: https://www.rd.usda.gov/about-rd/agencies/rural-business-cooperative-service")
    print("  Search for Iowa cooperatives and export results")
    return []


def search_ncua_credit_unions():
    """
    Search NCUA for Iowa credit unions.
    """
    print("\nNCUA Credit Union Search:")
    print("  Visit: https://mapping.ncua.gov/")
    print("  Filter by State: Iowa")
    print("  Export credit union list")
    return []


def search_electric_coops():
    """
    Search for Iowa electric cooperatives.
    """
    print("\nElectric Cooperatives:")
    print("  Visit: https://www.electric.coop/")
    print("  Or: Iowa Association of Electric Cooperatives")
    return []


def process_sos_export(filepath: str) -> list[dict]:
    """
    Process Iowa Secretary of State business search export.

    To get data:
    1. Go to: https://sos.iowa.gov/search/business/search.aspx
    2. Search for businesses containing "cooperative", "co-op", "credit union", etc.
    3. Export results to CSV
    4. Pass the CSV file path to this function
    """
    import csv

    candidates = []

    try:
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Business Name', row.get('Name', ''))
                if is_likely_cooperative(name):
                    candidates.append({
                        "name": name,
                        "location": row.get('City', '') + ", IA",
                        "source": "iowa_sos",
                        "status": row.get('Status', 'unknown'),
                        "website": None  # Would need to be looked up
                    })
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except Exception as e:
        print(f"Error processing file: {e}")

    return candidates


def create_sample_candidates():
    """
    Create sample candidates for testing the pipeline.
    These are potential cooperatives found through web searches.
    """
    # Sample candidates - these would normally come from SoS search or web scraping
    samples = [
        {
            "name": "Hawkeye Cooperative",
            "website": "https://www.hawkeyecooperative.com/",
            "location": "Iowa",
            "source": "web_search"
        },
        {
            "name": "Farmers Cooperative Association Stratford",
            "website": "https://www.stratfordcoop.com/",
            "location": "Stratford, IA",
            "source": "web_search"
        },
        {
            "name": "Ag Partners Cooperative",
            "website": "https://www.agpartnerscoop.com/",
            "location": "Iowa",
            "source": "web_search"
        },
        {
            "name": "Frontier Cooperative",
            "website": "https://www.frontiercoop.com/",
            "location": "Nebraska/Iowa",
            "source": "web_search"
        },
        {
            "name": "Prairie Energy Cooperative",
            "website": "https://www.prairieenergy.coop/",
            "location": "Clarion, IA",
            "source": "web_search"
        },
        {
            "name": "Maquoketa Valley Electric Cooperative",
            "website": "https://www.mvec.coop/",
            "location": "Anamosa, IA",
            "source": "web_search"
        },
        {
            "name": "T.I.P. Rural Electric Cooperative",
            "website": "https://www.tiprec.com/",
            "location": "Brooklyn, IA",
            "source": "web_search"
        },
        {
            "name": "Pella Cooperative Electric Association",
            "website": "https://www.pfrec.coop/",
            "location": "Pella, IA",
            "source": "web_search"
        },
        {
            "name": "Veridian Credit Union",
            "website": "https://www.veridiancu.org/",
            "location": "Waterloo, IA",
            "source": "web_search"
        },
        {
            "name": "Collins Community Credit Union",
            "website": "https://www.collinscu.org/",
            "location": "Cedar Rapids, IA",
            "source": "web_search"
        },
        {
            "name": "Decorah Bank and Trust Co",
            "website": "https://www.decorahbank.com/",
            "location": "Decorah, IA",
            "source": "web_search_control"  # Control - likely NOT a coop
        },
        {
            "name": "Fareway Stores",
            "website": "https://www.fareway.com/",
            "location": "Boone, IA",
            "source": "web_search_control"  # Control - NOT a coop
        }
    ]

    return samples


def deduplicate_candidates(candidates: list[dict], verified_names: set) -> list[dict]:
    """Remove candidates that match verified cooperatives."""
    deduped = []

    for c in candidates:
        name_normalized = normalize_name(c["name"])
        domain = extract_domain(c.get("website", "")) if c.get("website") else None

        # Check if already in verified list
        if name_normalized in verified_names:
            print(f"  Skipping (already verified): {c['name']}")
            continue
        if domain and domain in verified_names:
            print(f"  Skipping (domain match): {c['name']}")
            continue

        deduped.append(c)

    return deduped


def main():
    """Generate and save candidate cooperatives."""
    print("="*60)
    print("COOPERATIVE CANDIDATE GENERATOR")
    print("="*60)

    # Load verified cooperatives for deduplication
    print("\nLoading verified cooperatives...")
    verified_names = load_verified_cooperatives()
    print(f"Found {len(verified_names)} verified names/domains")

    # Print data source instructions
    print("\n" + "-"*60)
    print("DATA SOURCES")
    print("-"*60)
    search_usda_cooperatives()
    search_ncua_credit_unions()
    search_electric_coops()

    print("\nIowa Secretary of State:")
    print("  Visit: https://sos.iowa.gov/search/business/search.aspx")
    print("  Search for: 'cooperative', 'co-op', 'credit union'")
    print("  Export to CSV and process with: process_sos_export('path/to/file.csv')")

    # Create sample candidates for testing
    print("\n" + "-"*60)
    print("GENERATING SAMPLE CANDIDATES")
    print("-"*60)
    candidates = create_sample_candidates()
    print(f"Created {len(candidates)} sample candidates")

    # Deduplicate
    print("\nDeduplicating against verified cooperatives...")
    candidates = deduplicate_candidates(candidates, verified_names)
    print(f"After deduplication: {len(candidates)} candidates")

    # Save candidates
    print(f"\nSaving candidates to {CANDIDATES_FILE}")
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(candidates, f, indent=2)

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Review and edit candidates.json")
    print("2. Add more candidates from data sources above")
    print("3. Run: python scripts/similarity_search.py")
    print("="*60)


if __name__ == "__main__":
    main()

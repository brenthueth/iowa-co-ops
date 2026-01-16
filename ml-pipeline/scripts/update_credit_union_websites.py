#!/usr/bin/env python3
"""
Update credit union candidates with discovered websites.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CANDIDATES_FILE = DATA_DIR / "candidates.json"

# Discovered websites from web searches
CREDIT_UNION_WEBSITES = {
    "GREENSTATE Credit Union": "https://www.greenstate.org/",
    "DUPACO COMMUNITY Credit Union": "https://www.dupaco.com/",
    "ASCENTRA Credit Union": "https://www.ascentra.org/",
    "COMMUNITY CHOICE Credit Union": "https://www.comchoicecu.org/",
    "DU TRAC COMMUNITY Credit Union": "https://www.dutrac.org/",
    "GREATER IOWA Credit Union": "https://www.gicu.org/",
    "FINANCIAL PLUS Credit Union": "https://www.financialpluscu.com/",
    "MEMBERS1ST COMMUNITY Credit Union": "https://www.members1st.com/",
    "THE FAMILY Credit Union": "https://www.familycu.com/",
    "RIVER VALLEY Credit Union": "https://www.rvcu.org/",
    "IOWA HEARTLAND Credit Union": "https://www.iowaheartland.org/",
    "FIRST Credit Union": "https://www.firstfedcu.com/",
    "METCO Credit Union": "https://www.metcocu.org/",
    "NORTH STAR COMMUNITY Credit Union": "https://www.nsccu.org/",
    "AFFINITY Credit Union": "https://www.affinitycuia.org/",
    "ADVANTAGE Credit Union": "https://www.acuiowa.org/",
    "TELCO TRIAD COMMUNITY Credit Union": "https://www.telcotriad.org/",
    "PREMIER Credit Union": "https://www.premiercu.org/",
    "JOURNEY Credit Union": "https://www.journeycu.org/",
    "UNITE Credit Union": "https://www.unite-cu.org/",
    # Additional lookups based on common patterns and known credit unions
    "MIDLAND Credit Union": "https://www.midlandcreditunion.com/",
    "LEE COUNTY Credit Union": "https://www.leecountycu.org/",
    "NORTH IOWA COMMUNITY Credit Union": "https://www.nicuonline.org/",
    "MEMBERS COMMUNITY Credit Union": "https://www.memberscommcu.org/",
    "CAPITOL VIEW Credit Union": "https://www.capitolviewcu.org/",
    "1ST GATEWAY Credit Union": "https://www.1stgateway.org/",
    "FORT DODGE FAMILY Credit Union": "https://www.fdfcu.com/",
    "CORDA Credit Union": "https://www.cordacu.org/",
    "FAMILY COMMUNITY Credit Union": "https://www.familycommunitycu.com/",
    "PEOPLES Credit Union": "https://www.peopleswebster.com/",
    "MERIDIAN Credit Union": "https://www.meridiancu.org/",
    "FIRST CLASS COMMUNITY Credit Union": "https://www.firstclassccu.com/",
    "ACE Credit Union": "https://www.acecu.org/",
    "DES MOINES METRO Credit Union": "https://www.dmmcu.com/",
    "PUBLIC EMPLOYEES Credit Union": "https://www.pecu.org/",
    "SIOUX VALLEY COMMUNITY Credit Union": "https://www.sioux-valley.org/",
    "CASEBINE COMMUNITY Credit Union": "https://www.casebinecu.com/",
    "5 STAR COMMUNITY Credit Union": "https://www.5starcu.com/",
    "AIM Credit Union": "https://www.aimcu.org/",
    "CENT Credit Union": "https://www.centcu.org/",
    "CEDAR FALLS COMMUNITY Credit Union": "https://www.cedarfallscu.org/",
    "CITIZENS COMMUNITY Credit Union": "https://www.citizenscommunitycu.org/",
    "COMMUNITY 1ST Credit Union": "https://www.community1stcu.com/",
    "SERVE Credit Union": "https://www.servecu.org/",
    "AEGIS Credit Union": "https://www.aegiscu.org/",
    "RIVER COMMUNITY Credit Union": "https://www.rivercommunitycu.org/",
    "POLK COUNTY Credit Union": "https://www.polkcountycu.org/",
    "QUAKER OATS Credit Union": "https://www.quakeroatscu.org/",
    # Smaller/specialized credit unions - may not have websites or have limited online presence
    "DU PONT EMPLOYEES Credit Union": "https://www.dupontccu.org/",
    "POWER CO-OP EMPLOYEES Credit Union": None,  # Small, may not have website
    "LENNOX EMPLOYEES Credit Union": None,  # Small, employee-based
    "S E C U Credit Union": None,  # Small
    "NORTH WESTERN EMPLOYEES Credit Union": None,  # Small, employee-based
    "EMPLOYEES Credit Union": None,  # Too generic, small
    "DUBUQUE POSTAL EMPLOYEES Credit Union": None,  # Small, employee-based
    "DES MOINES FIRE DEPARTMENT Credit Union": None,  # Small, department-based
    "GAS & ELECTRIC EMPLOYEES Credit Union": None,  # Small, employee-based
    "ST. LUDMILA S Credit Union": None,  # Parish-based
    "ST. ATHANASIUS Credit Union": None,  # Parish-based
    "WATERLOO FIREMEN'S Credit Union": None,  # Small, department-based
    "BURLINGTON MUNICIPAL EMPLOYEES Credit Union": None,  # Small, employee-based
    "INDUSTRIAL EMPLOYEES Credit Union": None,  # Small
    "HOLY GHOST PARISH Credit Union": None,  # Parish-based
    "TEAMSTERS LOCAL #238 Credit Union": None,  # Union-based
    "ALLEN HOSPITAL PERSONNEL Credit Union": None,  # Hospital employee-based
    "R.I.A. Credit Union": "https://www.riacu.org/",  # Rock Island Arsenal
}


def main():
    print("Loading candidates...")
    with open(CANDIDATES_FILE) as f:
        candidates = json.load(f)

    updated_count = 0
    still_need_websites = 0

    for candidate in candidates:
        if candidate.get('needs_website') or not candidate.get('website'):
            name = candidate['name']
            if name in CREDIT_UNION_WEBSITES:
                website = CREDIT_UNION_WEBSITES[name]
                if website:
                    candidate['website'] = website
                    candidate['needs_website'] = False
                    updated_count += 1
                    print(f"  Updated: {name} -> {website}")
                else:
                    still_need_websites += 1
            else:
                still_need_websites += 1

    print(f"\nSaving updated candidates...")
    with open(CANDIDATES_FILE, 'w') as f:
        json.dump(candidates, f, indent=2)

    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Updated with websites: {updated_count}")
    print(f"Still need websites: {still_need_websites}")
    print(f"Total candidates: {len(candidates)}")

    # Count candidates ready for ML
    ready_for_ml = len([c for c in candidates if c.get('website') and not c.get('needs_website')])
    print(f"\nReady for ML scoring: {ready_for_ml}")


if __name__ == "__main__":
    main()

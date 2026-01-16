#!/usr/bin/env python3
"""
Update all cooperatives with discovered websites from research.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"

# All discovered websites from research
WEBSITES = {
    # MUTUAL INSURANCE - Batch 1
    "SECURITY MUTUAL INSURANCE ASSOCIATION": "https://www.securitymutualins.com/",
    "CENTURY MUTUAL INSURANCE ASSOCIATION": "http://www.centurymutualins.com/",
    "WELLABE MUTUAL HOLDING COMPANY": "https://www.wellabe.com/",
    "ALLIANCE MUTUAL INSURANCE ASSOCIATION": "https://alliancemutualins.com/",
    "WALCOTT MUTUAL INSURANCE ASSOCIATION": "http://www.walcottmutual.com/",
    "FARMERS MUTUAL INSURANCE ASSOCIATION OF MUSCATINE COUNTY": "https://www.muscatinemutual.com/",
    "MERCHANTS MUTUAL BONDING COMPANY": "https://www.merchantsbonding.com/",
    "FARMERS MUTUAL TELEPHONE COMPANY OF MOULTON": "https://www.farmersmutualcoop.com/",
    "SHELBY COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.shelbycountyfarmers.com/",
    "GRUNDY MUTUAL INSURANCE ASSOCIATION": "https://www.grundymutual.com/",
    "FARMERS MUTUAL INSURANCE ASSOCIATION OF LINN COUNTY": "https://fmilc.com/",
    "HEARTLAND MUTUAL INSURANCE ASSOCIATION": "https://www.heartlandmutual.com/",
    "FAYETTE COUNTY MUTUAL INSURANCE ASSOCIATION": "http://farmersmutualfayette.com/",

    # MUTUAL INSURANCE - Batch 2
    "HUMBOLDT COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.humboldtmutualinsurance.com/",
    "FLOYD COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.floydcountymutual.com/",
    "JASPER COUNTY MUTUAL INSURANCE ASSOCIATION": "https://jaspercountymutual.net/",
    "LEE COUNTY MUTUAL INSURANCE ASSOCIATION": "https://leecountymutual.com/",
    "BREMER COUNTY MUTUAL INSURANCE ASSOCIATION": "https://bremermutual.com/",
    "POCAHONTAS COUNTY MUTUAL INSURANCE ASSOCIATION": "https://pocahontasmutualinsurance.com/",
    "LOUISA COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.louisamutual.com/",
    "CHICKASAW COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.chickasawmutualinsurance.com/",
    "HOWARD COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.hcmcresco.com/",
    "POWESHIEK COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.poweshiekmutualinsurance.com/",
    "TAMA COUNTY MUTUAL INSURANCE ASSOCIATION": "https://www.tamacountymutual.com/",
    "DES MOINES COUNTY MUTUAL INSURANCE ASSOCIATION": "https://dmcmutual.com/",

    # AGRICULTURAL - Batch 1
    "ASSOCIATED MILK PRODUCERS, INC.": "https://www.ampi.com/",
    "OSAGE COOPERATIVE ELEVATOR": "https://osagecoop.com/",
    "SIOUX HONEY ASSOCIATION, COOPERATIVE": "https://siouxhoney.com/",
    "PRODUCERS COOPERATIVE COMPANY": "https://gazaproducerscoop.com/",
    "IOWA FARM BUREAU FEDERATION": "https://www.iowafarmbureau.com/",
    "QUAD COUNTY CORN PROCESSORS COOPERATIVE": "https://www.quad-county.com/",
    "LITTLE SIOUX CORN PROCESSORS COOPERATIVE LLC": "https://littlesiouxcornprocessors.com/",
    "COOPERATIVE PRODUCERS, INC.": "https://cpicoop.com/",
    "FARMERS CO-OP SOCIETY OF SIOUX CENTER": "https://www.farmerscoopsociety.com/",
    "NORTHEAST IOWA DAIRY FOUNDATION": "https://iowadairycenter.com/",
    "CORN PLUS COOPERATIVE": "https://www.cornplus.com/",
    "CORN LP": "https://www.cornlp.com/",
    "FARMERS UNION COOPERATIVE": "https://www.farmerunion.net/",
    "FREEBORN COOPERATIVE OIL COMPANY": "https://freeborncountycoop.com/",
    "AGRILAND FS COOPERATIVE": "https://www.agrilandfs.com/",

    # AGRICULTURAL - Batch 2
    "AGSTATE COOPERATIVE": "https://agstate.org/",
    "FIRST COOPERATIVE ASSOCIATION": "https://agstate.org/",
    "TAMA-BENTON COOPERATIVE COMPANY": "https://www.tamabentoncoop.com/",
    "FCS COOPERATIVE": "https://www.farmerscoopsociety.com/",
    "ASPINWALL COOPERATIVE CO.": "http://www.aspinwallcoop.com/",
    "BUCKINGHAM CO-OPERATIVE CO.": "http://buckingham.coop/",
    "EAGLE GROVE COOPERATIVE": "https://www.goldeaglecoop.com/",
    "GOLDFIELD COOPERATIVE": "https://www.goldeaglecoop.com/",
    "HULL COOPERATIVE ASSOCIATION": "https://www.hullcoop.com/",
    "WEST CENTRAL COOPERATIVE": "https://www.landus.ag/",
    "FARMERS CO-OPERATIVE ELEVATOR": "https://www.coopfe.com/",
    "NORTH IOWA COOPERATIVE GRAIN COMPANY": "https://www.nicoop.com/",

    # ELECTRIC - Batch 1
    "NORTHWEST IOWA POWER COOPERATIVE": "https://www.nipco.coop/",
    "ATCHISON-HOLT ELECTRIC COOPERATIVE": "https://www.ahec.coop/",
    "GRUNDY COUNTY RURAL ELECTRIC COOPERATIVE": "https://www.grundycountyrecia.com/",
    "FARMERS ELECTRIC COOPERATIVE": "https://www.farmersrec.com/",
    "BUTLER COUNTY RURAL ELECTRIC COOPERATIVE": "https://butlerrec.coop/",
    "GUTHRIE COUNTY RURAL ELECTRIC COOPERATIVE ASSOCIATION": "https://www.guthrie-rec.coop/",
    "FRANKLIN RURAL ELECTRIC COOPERATIVE": "https://www.franklinrec.coop/",
    "FEDERATED RURAL ELECTRIC ASSOCIATION": "https://federatedrea.coop/",
    "CORN BELT POWER COOPERATIVE": "https://www.cbpower.coop/",
    "EAST-CENTRAL IOWA RURAL ELECTRIC COOPERATIVE": "https://ecirec.coop/",
    "MIDLAND POWER COOPERATIVE": "https://www.midlandpower.coop/",
    "NORTH WEST RURAL ELECTRIC COOPERATIVE": "https://www.nwrec.coop/",
    "SOUTHWEST IOWA RURAL ELECTRIC COOPERATIVE": "https://swiarec.coop/",
    "T.I.P. RURAL ELECTRIC COOPERATIVE": "https://tiprec.com/",
    "WESTERN IOWA POWER COOPERATIVE": "https://www.wipco.com/",
    "IOWA LAKES ELECTRIC COOPERATIVE": "https://www.ilec.coop/",
    "CHARITON VALLEY ELECTRIC COOPERATIVE": "https://www.cvrec.com/",
    "SOUTHERN IOWA ELECTRIC COOPERATIVE": "https://www.sie.coop/",
    "ALLAMAKEE-CLAYTON ELECTRIC COOPERATIVE": "https://acrec.com/",
    "CLARKE ELECTRIC COOPERATIVE": "https://www.cecnet.net/",
    "MAQUOKETA VALLEY ELECTRIC COOPERATIVE": "https://www.mvec.coop/",
    "NISHNABOTNA VALLEY RURAL ELECTRIC COOPERATIVE": "https://www.nvrec.com/",

    # ELECTRIC - Batch 2
    "WINNEBAGO COOPERATIVE TELECOM ASSOCIATION": "https://wctatel.net/",
    "FREEBORN-MOWER COOPERATIVE SERVICES": "https://fmec.coop/",
    "HEARTLAND POWER COOPERATIVE": "https://heartlandpower.com/",
    "LINN COUNTY RURAL ELECTRIC COOPERATIVE": "https://www.linncountyrec.com/",
    "LYON RURAL ELECTRIC COOPERATIVE": "https://lyonrec.coop/",
    "OSCEOLA ELECTRIC COOPERATIVE": "https://osceolaelectric.com/",
    "PELLA COOPERATIVE ELECTRIC ASSOCIATION": "https://pella-cea.org/",
    "RACCOON VALLEY ELECTRIC COOPERATIVE": "https://www.rvec.coop/",
    "SIOUXLAND ENERGY COOPERATIVE": "https://www.siouxlandenergy.com/",
    "STANHOPE COOPERATIVE TELEPHONE ASSOCIATION": "https://www.cooptelexchange.com/",

    # TELECOM - Batch 1
    "COOPERATIVE TELEPHONE EXCHANGE": "https://www.cooptelexchange.com/",
    "VAN HORNE COOPERATIVE TELEPHONE COMPANY": "https://vanhornecommunications.com/",
    "SPRINGVILLE COOPERATIVE TELEPHONE ASSOCIATION": "https://springvilletelephone.com/",
    "MARTELLE COOPERATIVE TELEPHONE ASSOCIATION": "https://martellecom.us/",
    "RIVER VALLEY TELECOMMUNICATIONS COOP": "https://rvtc.net/",
    "MABEL COOPERATIVE TELEPHONE COMPANY": "https://www.mabeltel.coop/",
    "WEBSTER-CALHOUN COOPERATIVE TELEPHONE ASSOCIATION": "https://www.wccta.com/",
    "PARTNER COMMUNICATIONS COOPERATIVE": "https://www.pcctel.net/",
    "COOPERATIVE TELEPHONE COMPANY": "https://www.ctctechnology.net/",
    "FENTON COOPERATIVE TELEPHONE COMPANY": "https://www.fentontelephone.com/",
    "FARMERS COOPERATIVE TELEPHONE COMPANY": "https://fctc.coop/",
    "CLARENCE TELEPHONE COMPANY, INC. (COOPERATIVE)": "https://clarencetelinc.com/",
    "BERNARD TELEPHONE COMPANY COOPERATIVE": "https://bernardtelephone.com/",
    "LONG LINES LTD": "https://www.longlines.com/",
    "FARMERS MUTUAL TELEPHONE COMPANY OF SHELLSBURG": "https://usacomm.coop/",
    "KALONA COOPERATIVE TELEPHONE COMPANY": "https://www.kctc.net/",
    "WELLSBURG COOPERATIVE TELEPHONE ASSOCIATION": "https://heartofiowa.coop/",
    "FARMERS AND MERCHANTS MUTUAL TELEPHONE COMPANY": "https://www.kctc.net/",
    "WEST LIBERTY TELEPHONE COMPANY COOPERATIVE": "https://libertycommunications.com/",
    "MECHANICSVILLE TELEPHONE COMPANY": "https://mechanicsvillefiber.com/",
    "NORTH ENGLISH COOPERATIVE TELEPHONE COMPANY": "https://northenglishtelephone.com/",

    # TELECOM - Batch 2
    "READLYN TELEPHONE COMPANY": "https://readlyntelco.com/",
    "KEYSTONE-NORWAY COOPERATIVE TELEPHONE COMPANY": "https://keystonecommunications.com/",
    "LAMOTTE TELEPHONE COMPANY COOPERATIVE": "https://lamotte-telco.com/",
    "MT. VERNON COOPERATIVE TELEPHONE COMPANY": "https://southslope.com/",
    "DANVILLE MUTUAL TELEPHONE COMPANY": "https://danvilletelco.net/",
    "FARMERS TELEPHONE COMPANY (ESSEX)": "https://heartland.net/",
    "WALNUT TELEPHONE COMPANY": "https://www.metc.net/",
    "SCRANTON TELEPHONE COMPANY": "https://www.scrantontelephone.com/",
    "MINBURN TELEPHONE COMPANY COOPERATIVE": "https://minburncomm.com/",
    "ATKINS TELEPHONE COMPANY": "https://atccomm.net/",
    "INTERSTATE TELECOMMUNICATIONS COOPERATIVE": "https://www.itc-web.com/",
    "LYNNVILLE COOPERATIVE TELEPHONE COMPANY": "https://lynnvilletel.com/",
    "HUBBARD COOPERATIVE TELEPHONE ASSOCIATION": "https://hubbardtelephone.net/",
    "PALMER MUTUAL TELEPHONE COMPANY": "https://palmerone.com/",
    "CENTER JUNCTION TELEPHONE COMPANY, INC.": "https://centerjunctiontelephone.com/",
    "MONONA COOPERATIVE TELEPHONE COMPANY": "https://www.neitel.com/",
    "MONTEZUMA MUTUAL TELEPHONE COMPANY": "https://www.mahaska.org/montezuma",

    # ENERGY
    "COMMUNITY OIL COMPANY, A COOPERATIVE": "https://communityoilco.com/",
    "HANCOCK COUNTY COOPERATIVE OIL ASSOCIATION": "https://www.hancockcountycoop.com/",
    "COOPERATIVE ENERGY COMPANY": "https://www.coopenergyco.com/",
    "CONSUMERS ENERGY COOPERATIVE": "https://www.consumersenergy.coop/",
    "COOPERATIVE GAS AND OIL COMPANY": "http://www.coopgassc.com/",
    "LINN COOPERATIVE OIL COMPANY": "https://www.linncoop.com/",
    "W & H COOPERATIVE OIL COMPANY": "https://www.whcoop.com/",
    "WARREN COUNTY OIL COOPERATIVE ASSOCIATION": "https://warrencountyoil.com/",
    "SIOUXLAND ETHANOL COOPERATIVE": "https://www.siouxlandenergy.com/",
    "THE CONSUMERS COOPERATIVE SOCIETY": "https://consumerscoop.net/",

    # FOOD
    "ONEOTA COMMUNITY COOPERATIVE": "https://oneotacoop.com/",
    "NEW PIONEER'S COOPERATIVE SOCIETY": "https://www.newpi.coop/",
    "PRODUCERS LIVE STOCK MARKETING ASSOCIATION": "https://producers-livestock.com/",
    "ROOTED CARROT COOPERATIVE MARKET": "https://rootedcarrot.coop/",
    "NATIONAL COOPERATIVE GROCERS ASSOCIATION": "https://www.ncg.coop/",
    "FRONTIER COOPERATIVE": "https://www.frontiercoop.com/",

    # OTHER/PURCHASING/HEALTH
    "FREMONT FUNERAL CHAPEL COOPERATIVE": "https://www.fremontfuneralchapel.com/",
    "HEALTH ENTERPRISES COOPERATIVE": "https://healthenterprises.org/",
    "O'BRIEN COOPERATIVE FUNERAL ASSOCIATION": "https://sanborn-hartleyfuneralhomes.com/",
    "AMERICAN PHARMACY COOPERATIVE, INC.": "https://www.apcinet.com/",
    "EMPLOYER HEALTH CARE ALLIANCE COOPERATIVE": "https://the-alliance.org/",
    "NATIONAL BLOOD TESTING COOPERATIVE": "https://nbtc.coop/",
    "HEALTH ACCESS COOPERATIVE": "https://healthaccesscooperative.com/",
    "COOPERATIVE RESPONSE CENTER, INC.": "https://www.crc.coop/",
    "THE COOPERATIVE FINANCE ASSOCIATION, INC.": "https://cfafs.com/",
    "NATIONAL INFORMATION SOLUTIONS COOPERATIVE, INC": "https://www.nisc.coop/",
    "QCS PURCHASING COOPERATIVE": "https://qcspurchasing.com/",

    # CREDIT
    "IOWA CREDIT UNION LEAGUE": "https://www.iowacreditunions.com/",
    "IOWA CREDIT UNION FOUNDATION, INC": "https://www.iowacreditunionfoundation.org/",
    "CREDIT UNION NATIONAL ASSOCIATION, INC.": "https://www.cuna.org/",
    "THE CREDIT UNION LOAN SOURCE LLC": "https://www.buyculsloans.com/",
    "ENT CREDIT UNION": "https://www.ent.com/",
}


def normalize_name(name: str) -> str:
    """Normalize name for matching."""
    return name.lower().strip().replace(",", "").replace(".", "")


def main():
    print("Loading labeled data...")
    with open(LABELED_DATA_PATH) as f:
        data = json.load(f)

    # Create lookup by normalized name
    website_lookup = {normalize_name(k): v for k, v in WEBSITES.items()}

    updated = 0
    already_had = 0
    not_found = 0

    for coop in data['verified_cooperatives']:
        if coop.get('website'):
            already_had += 1
            continue

        norm_name = normalize_name(coop['name'])
        if norm_name in website_lookup:
            coop['website'] = website_lookup[norm_name]
            updated += 1
            print(f"  Updated: {coop['name']}")
        else:
            not_found += 1

    data['metadata']['last_updated'] = datetime.now().isoformat()

    print(f"\nSaving to {LABELED_DATA_PATH}...")
    with open(LABELED_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2)

    # Count final stats
    with_website = len([c for c in data['verified_cooperatives'] if c.get('website')])
    without_website = len([c for c in data['verified_cooperatives'] if not c.get('website')])

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Already had website: {already_had}")
    print(f"Updated with website: {updated}")
    print(f"No website found: {not_found}")
    print()
    print(f"Total with website: {with_website}")
    print(f"Total without website: {without_website}")
    print(f"Coverage: {with_website}/{len(data['verified_cooperatives'])} ({100*with_website/len(data['verified_cooperatives']):.1f}%)")


if __name__ == "__main__":
    main()

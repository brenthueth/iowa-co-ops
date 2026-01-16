# Iowa Cooperatives Project

## Overview
Interactive visual directory of Iowa cooperatives displayed as a collage of website screenshots. Built for ISU research on cooperative businesses in Iowa.

**Live site:** https://brenthueth.github.io/iowa-co-ops/

## Project Structure

```
iowa-co-ops/
├── index.html              # Main website (single-page app)
├── screenshots/            # Cooperative website screenshots (001.png - 209.png)
├── CLAUDE.md               # This file - project context for Claude
├── README.md               # Project documentation
└── ml-pipeline/            # ML-based cooperative discovery system
    ├── METHODOLOGY.md      # Detailed methodology documentation
    ├── data/
    │   ├── labeled_data.json           # Central database (412 cooperatives)
    │   ├── verified_cooperatives.json  # All verified cooperatives
    │   ├── verified_with_websites.json # 202 cooperatives with websites
    │   ├── sos_candidates.json         # Iowa Secretary of State candidates
    │   └── similarity_results.json     # ML similarity scores
    └── scripts/
        ├── batch_import_all.py         # Import cooperatives to website
        ├── verify_candidates.py        # Manual verification CLI
        ├── similarity_search.py        # Embedding-based discovery
        └── fetch_candidates.py         # Fetch candidate data
```

## Current State

### Statistics
- **Total verified cooperatives:** 412
- **With websites:** 202
- **On live site:** 209 (with screenshots)

### Categories
| Category | Count |
|----------|-------|
| Agricultural | 103 |
| Electric | 82 |
| Mutual Insurance | 81 |
| Telecom | 57 |
| Credit Unions | 42 |
| Energy | 15 |
| Other | 15 |
| Food | 11 |
| Purchasing | 6 |

### Data Sources
1. **Iowa Institute for Cooperatives** (86) - Seed data from iowa.coop
2. **Iowa Secretary of State** (278) - Business registry filtering
3. **ML Pipeline** (48) - NCUA, IAEC, similarity search

## Technical Details

### Website (index.html)
- **Layout:** Masonry grid with responsive columns (3-14 based on viewport)
- **Colors:** ISU Cyclone theme (Cardinal #C8102E, Gold #F1BE48)
- **Features:** Category filtering, zoom/pan, click to visit sites
- **Card sizes:** 140-250px width, 120-160px height

### ML Pipeline
- **Embedding model:** sentence-transformers/all-MiniLM-L6-v2
- **Similarity threshold:** 0.5 for manual review
- **Precision:** 98% (49 verified, 1 rejected)

### Screenshots
- Captured with Puppeteer (headless Chrome)
- 1280x800 viewport, 2s wait after load
- Zero-padded filenames (001.png, 002.png, etc.)

## Common Tasks

### Add new cooperatives
```bash
cd ml-pipeline
python scripts/verify_candidates.py    # Manual verification
python scripts/batch_import_all.py     # Import to website
```

### Update website layout
Edit `index.html` - key sections:
- CSS variables at `:root` (colors, sizing)
- `getResponsiveConfig()` function (column counts)
- `HEIGHT_VARIANTS` array (card heights)

## Potential Future Work
- Website validation (check for dead links)
- Additional data sources (USDA cooperative directory)
- Subcategories for large groups (agricultural types)
- Search functionality
- Cooperative detail pages
- Add similar pages for other states 
- Building national directory 
- Expand to MGO class with cooperatives as subcategory

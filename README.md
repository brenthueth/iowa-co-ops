# Iowa Cooperatives Directory

A visual directory of Iowa cooperatives, displayed as a collage of website screenshots. This project combines manual curation with machine learning to discover and verify cooperatives across the state.

**Live site:** [View the directory](https://brenthueth.github.io/iowa-co-ops/)

## Overview

This project catalogs Iowa's cooperative organizations across multiple sectors:

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
| **Total** | **412** |

Of these, 203 cooperatives with active websites are featured on the visual directory.

## Data Sources

Cooperatives were identified from three primary sources:

### 1. Iowa Institute for Cooperatives (86 cooperatives)
The original seed dataset of known Iowa cooperatives, manually curated with verified websites.

### 2. Iowa Secretary of State Business Registry (278 cooperatives)
Active business entities from [data.iowa.gov](https://data.iowa.gov/Regulation/Active-Iowa-Business-Entities/ez5t-3qay) filtered by:
- Corporation types: `CO-OP STOCK`, `CO-OP NON STOCK`, `DOMESTIC COOPERATIVE`, `CO-OP STOCK VALUE ADDED`
- Name patterns containing cooperative-related keywords
- Exclusion of housing cooperatives and merger shell companies

### 3. ML Pipeline Discovery (48 cooperatives)
Additional cooperatives discovered through:
- NCUA credit union database
- Iowa Association of Electric Cooperatives member list
- Web search and similarity scoring

## Methodology

For details on the machine learning pipeline and manual review process, see [ML Pipeline Methodology](ml-pipeline/METHODOLOGY.md).

## Project Structure

```
iowa-co-ops/
├── index.html              # Main website
├── screenshots/            # Cooperative website screenshots
├── ml-pipeline/            # ML-based discovery system
│   ├── data/               # JSON data files
│   ├── scripts/            # Processing scripts
│   └── METHODOLOGY.md      # Detailed methodology
└── README.md               # This file
```

## Development

### Prerequisites
- Python 3.8+
- Node.js (for Puppeteer screenshots)

### Running the ML Pipeline

```bash
cd ml-pipeline

# Process new candidates
python scripts/fetch_candidates.py

# Run similarity search
python scripts/similarity_search.py

# Manual verification
python scripts/verify_candidates.py

# Import to website
python scripts/batch_import_all.py
```

## License

This project is for educational and research purposes.

## Acknowledgments

- Iowa Institute for Cooperatives for the initial dataset
- Iowa Secretary of State for open business entity data
- NCUA for credit union data

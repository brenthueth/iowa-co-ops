# ML Pipeline Methodology

This document describes the machine learning pipeline and manual review process used to discover and verify Iowa cooperatives.

## Overview

The pipeline uses a combination of:
1. **Multiple data sources** for candidate generation
2. **Sentence embeddings** for similarity-based discovery
3. **Human-in-the-loop verification** for quality assurance
4. **Active learning** to improve over time

## Data Sources

### 1. Iowa Institute for Cooperatives (Seed Data)
- **Count:** 86 cooperatives
- **Source:** Manual curation from [iowa.coop](https://iowa.coop)
- **Quality:** High - verified cooperatives with websites
- **Usage:** Training data for similarity model

### 2. Iowa Secretary of State Business Registry
- **Count:** 278 cooperatives identified
- **Source:** [data.iowa.gov](https://data.iowa.gov/Regulation/Active-Iowa-Business-Entities/ez5t-3qay)
- **Dataset size:** 318,944 active Iowa businesses
- **Filtering criteria:**
  - Corporation types explicitly indicating cooperatives:
    - `CO-OP STOCK`
    - `CO-OP NON STOCK`
    - `DOMESTIC COOPERATIVE`
    - `CO-OP STOCK VALUE ADDED`
  - Name patterns: "cooperative", "co-op", "credit union", etc.
  - Exclusions: housing cooperatives, HOAs, merger shell companies

### 3. NCUA Credit Union Database
- **Count:** 68 Iowa credit unions
- **Source:** [NCUA.gov](https://ncua.gov) quarterly data
- **Quality:** Authoritative federal data
- **Fields used:** Name, city, website, asset size

### 4. Iowa Association of Electric Cooperatives
- **Count:** 37 electric cooperatives
- **Source:** [IAEC member directory](https://www.iaec.coop)
- **Quality:** High - verified member list

## Similarity Search Pipeline

### Embedding Model
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding dimension:** 384
- **Why this model:** Fast, accurate, good for semantic similarity

### Process

1. **Content Extraction**
   - Fetch homepage content from cooperative websites
   - Extract text using `trafilatura` library
   - Clean and normalize text

2. **Embedding Generation**
   - Generate embeddings for all verified cooperative content
   - Create reference embedding (mean of verified cooperatives)

3. **Candidate Scoring**
   - Generate embeddings for candidate websites
   - Calculate cosine similarity to reference
   - Rank candidates by similarity score

4. **Threshold Selection**
   - Candidates with score >= 0.5 proceed to manual review
   - Lower threshold captures more candidates at cost of precision

## Manual Review Process

### Verification CLI (`verify_candidates.py`)

Interactive command-line tool for human review:

```
================================================================================
CANDIDATE 1/10
================================================================================
Name: Example Cooperative
Website: https://example.coop
Category: agricultural
Similarity Score: 0.723
Source: ncua

Website Content Preview:
  Welcome to Example Cooperative, serving Iowa farmers since 1920...

--------------------------------------------------------------------------------
Decision: [v]erify, [r]eject, [s]kip, [o]pen in browser, [q]uit:
```

### Review Guidelines
- **Verify:** Organization is clearly a cooperative
- **Reject:** Not a cooperative (false positive)
- **Skip:** Uncertain, needs more research

### Precision Tracking

The system tracks precision over time:

| Session | Verified | Rejected | Precision |
|---------|----------|----------|-----------|
| 1 | 6 | 0 | 100% |
| 2 | 10 | 0 | 100% |
| 3 | 15 | 0 | 100% |
| 4 | 18 | 1 | 95% |
| **Total** | **49** | **1** | **98%** |

## Category Classification

Cooperatives are classified into categories based on:
1. **Name keywords:** "electric", "telephone", "credit union", etc.
2. **Corporation type:** From SoS data
3. **Website content:** Manual review

### Categories

| Category | Description | Count |
|----------|-------------|-------|
| agricultural | Grain elevators, farm supply, dairy | 103 |
| electric | Rural electric cooperatives | 82 |
| mutual | Mutual insurance associations | 81 |
| telecom | Telephone and communications | 57 |
| credit | Credit unions | 42 |
| energy | Oil, propane, ethanol | 15 |
| other | Miscellaneous (funeral, health, etc.) | 15 |
| food | Food co-ops, grocery | 11 |
| purchasing | Purchasing cooperatives | 6 |

## Website Import Process

### Screenshot Capture
- **Tool:** Puppeteer (headless Chrome)
- **Viewport:** 1280x800
- **Wait time:** 2 seconds after page load
- **Timeout:** 30 seconds per site

### Import Script (`batch_import_all.py`)
1. Compare verified cooperatives against existing website entries
2. Assign sequential IDs
3. Capture screenshots for new entries
4. Update `index.html` with new cooperative data
5. Mark cooperatives as exported in database

## Data Files

### `labeled_data.json`
Central database containing:
- All verified cooperatives
- Rejected candidates
- Precision statistics
- Metadata

### `verified_cooperatives.json`
All 412 verified cooperatives (with and without websites)

### `verified_with_websites.json`
202 cooperatives with active websites, ready for import

### `sos_candidates.json`
Candidates extracted from Iowa SoS data

### `similarity_results.json`
ML pipeline candidates with similarity scores

## Quality Assurance

### Deduplication
- Cooperatives are deduplicated by website URL
- Prefer original iowa_institute entries over duplicates
- Handle merged cooperatives (e.g., AgState = First Cooperative + ALCECO)

### Exclusion Rules
- Housing cooperatives and HOAs
- Merger shell companies
- Non-Iowa entities
- Defunct organizations

## Future Improvements

1. **Website validation:** Periodic checks for dead links
2. **Content updates:** Re-fetch and re-score periodically
3. **New sources:** Farm Bureau data, USDA cooperative directory
4. **Category refinement:** Subcategories for large groups

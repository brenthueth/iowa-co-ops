#!/usr/bin/env python3
"""
Scrape text content from cooperative websites.
Uses trafilatura for clean text extraction.

Can scrape either verified cooperatives or candidates.
Usage:
    python scrape_websites.py              # Scrape verified cooperatives
    python scrape_websites.py --candidates # Scrape candidates with websites
"""

import json
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import trafilatura
from tqdm import tqdm

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
COOPS_FILE = DATA_DIR / "verified_cooperatives.json"
CANDIDATES_FILE = DATA_DIR / "candidates.json"
OUTPUT_FILE = DATA_DIR / "cooperative_content.json"
CANDIDATES_OUTPUT_FILE = DATA_DIR / "candidate_content.json"

# Request settings
TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}


def fetch_url(url: str) -> str | None:
    """Fetch HTML content from URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def extract_text(html: str, url: str) -> str | None:
    """Extract main text content from HTML using trafilatura."""
    try:
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=False,
            url=url
        )
        return text
    except Exception as e:
        print(f"  Error extracting text: {e}")
        return None


def scrape_cooperative(coop: dict, is_candidate: bool = False) -> dict:
    """Scrape a single cooperative website."""
    result = {
        "name": coop["name"],
        "website": coop["website"],
        "location": coop.get("location", "Iowa"),
        "source": coop.get("source", "unknown"),
        "content": None,
        "content_length": 0,
        "success": False
    }

    # Add fields that exist in verified cooperatives
    if not is_candidate:
        result["id"] = coop.get("id")
        result["category"] = coop.get("category")
        result["type"] = coop.get("type")

    html = fetch_url(coop["website"])
    if html:
        text = extract_text(html, coop["website"])
        if text and len(text.strip()) > 50:  # Minimum content threshold
            result["content"] = text.strip()
            result["content_length"] = len(text)
            result["success"] = True

    return result


def main():
    """Main scraping pipeline."""
    parser = argparse.ArgumentParser(description="Scrape cooperative websites")
    parser.add_argument("--candidates", action="store_true", help="Scrape candidates instead of verified")
    args = parser.parse_args()

    if args.candidates:
        print("Loading candidates...")
        with open(CANDIDATES_FILE) as f:
            all_candidates = json.load(f)
        # Filter to only candidates with websites
        cooperatives = [c for c in all_candidates if c.get("website") and not c.get("needs_website")]
        output_file = CANDIDATES_OUTPUT_FILE
        is_candidate = True
        print(f"Found {len(cooperatives)} candidates with websites to scrape\n")
    else:
        print("Loading verified cooperatives...")
        with open(COOPS_FILE) as f:
            cooperatives = json.load(f)
        output_file = OUTPUT_FILE
        is_candidate = False
        print(f"Found {len(cooperatives)} cooperatives to scrape\n")

    results = []
    successful = 0

    # Process sequentially to be respectful of servers
    for coop in tqdm(cooperatives, desc="Scraping websites"):
        result = scrape_cooperative(coop, is_candidate)
        results.append(result)

        if result["success"]:
            successful += 1

        # Small delay between requests
        time.sleep(0.5)

    # Save results
    print(f"\nSaving results to {output_file}")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Total: {len(cooperatives)}")
    print(f"Successfully scraped: {successful}")
    print(f"Failed: {len(cooperatives) - successful}")

    # Content stats
    content_lengths = [r["content_length"] for r in results if r["success"]]
    if content_lengths:
        print(f"\nContent statistics:")
        print(f"  Average length: {sum(content_lengths) // len(content_lengths):,} chars")
        print(f"  Min length: {min(content_lengths):,} chars")
        print(f"  Max length: {max(content_lengths):,} chars")

    # List failures
    failures = [r for r in results if not r["success"]]
    if failures:
        print(f"\nFailed sites:")
        for fail in failures:
            print(f"  - {fail['name']} ({fail['website']})")


if __name__ == "__main__":
    main()

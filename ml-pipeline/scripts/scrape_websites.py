#!/usr/bin/env python3
"""
Scrape text content from verified cooperative websites.
Uses trafilatura for clean text extraction.
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import trafilatura
from tqdm import tqdm

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
COOPS_FILE = DATA_DIR / "verified_cooperatives.json"
OUTPUT_FILE = DATA_DIR / "cooperative_content.json"

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


def scrape_cooperative(coop: dict) -> dict:
    """Scrape a single cooperative website."""
    result = {
        "id": coop["id"],
        "name": coop["name"],
        "website": coop["website"],
        "category": coop["category"],
        "type": coop["type"],
        "location": coop["location"],
        "content": None,
        "content_length": 0,
        "success": False
    }

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
    print("Loading verified cooperatives...")
    with open(COOPS_FILE) as f:
        cooperatives = json.load(f)

    print(f"Found {len(cooperatives)} cooperatives to scrape\n")

    results = []
    successful = 0

    # Process sequentially to be respectful of servers
    for coop in tqdm(cooperatives, desc="Scraping websites"):
        result = scrape_cooperative(coop)
        results.append(result)

        if result["success"]:
            successful += 1

        # Small delay between requests
        time.sleep(0.5)

    # Save results
    print(f"\nSaving results to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Total cooperatives: {len(cooperatives)}")
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
        for f in failures:
            print(f"  - {f['name']} ({f['website']})")


if __name__ == "__main__":
    main()

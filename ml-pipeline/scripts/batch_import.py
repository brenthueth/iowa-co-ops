#!/usr/bin/env python3
"""
Batch import verified cooperatives into the website.

This script:
1. Reads newly verified cooperatives from labeled_data.json
2. Captures screenshots using Puppeteer
3. Updates index.html with new cooperative entries
4. Marks cooperatives as exported

Usage:
    python batch_import.py [--dry-run] [--min-score S]

Options:
    --dry-run       Show what would be imported without making changes
    --min-score S   Only import cooperatives with score >= S (default: 0.5)
"""

import json
import argparse
import subprocess
import re
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ML_PIPELINE_DIR = Path(__file__).parent.parent
DATA_DIR = ML_PIPELINE_DIR / "data"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"
INDEX_HTML_PATH = PROJECT_ROOT / "index.html"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    """Save JSON file with pretty formatting."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_exportable_cooperatives(labeled_data, min_score=0.5):
    """Get cooperatives that are ready to export."""
    exportable = []
    for coop in labeled_data['verified_cooperatives']:
        # Only export ML-discovered cooperatives (not original 86)
        if coop.get('source') == 'ml_pipeline':
            # Check if already exported
            if not coop.get('exported_to_website'):
                # Check minimum score
                score = coop.get('similarity_score', 1.0)
                if score >= min_score:
                    exportable.append(coop)
    return exportable


def capture_screenshot(coop, screenshots_dir):
    """Capture screenshot for a cooperative using Node.js script."""
    # Create a temporary script to capture single screenshot
    script = f"""
const puppeteer = require('puppeteer');

async function capture() {{
    const browser = await puppeteer.launch({{
        headless: true,
        channel: 'chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }});

    const page = await browser.newPage();
    await page.setViewport({{ width: 1280, height: 800 }});
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');

    try {{
        await page.goto('{coop["website"]}', {{
            waitUntil: 'networkidle2',
            timeout: 30000
        }});
        await page.waitForTimeout(2000);

        const filename = '{coop["id"]}.png';
        await page.screenshot({{
            path: '{screenshots_dir}/' + filename,
            fullPage: false
        }});
        console.log('SUCCESS: ' + filename);
    }} catch (error) {{
        console.log('ERROR: ' + error.message);
    }}

    await browser.close();
}}

capture();
"""

    # Write temporary script
    temp_script = PROJECT_ROOT / '_temp_capture.js'
    with open(temp_script, 'w') as f:
        f.write(script)

    try:
        result = subprocess.run(
            ['node', str(temp_script)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=60
        )
        success = 'SUCCESS' in result.stdout
        if not success:
            print(f"  Screenshot error: {result.stdout.strip()} {result.stderr.strip()}")
        return success
    except subprocess.TimeoutExpired:
        print(f"  Screenshot timeout")
        return False
    finally:
        temp_script.unlink(missing_ok=True)


def get_current_max_id(index_html_content):
    """Extract the current maximum ID from index.html."""
    # Find all id values in the cooperatives array
    id_matches = re.findall(r'\{\s*id:\s*(\d+)', index_html_content)
    if id_matches:
        return max(int(id) for id in id_matches)
    return 0


def generate_coop_entry(coop):
    """Generate JavaScript object entry for a cooperative."""
    # Escape quotes in name
    name = coop['name'].replace("'", "\\'")
    category = coop['category']
    website = coop['website']

    return f"        {{ id: {coop['id']}, name: '{name}', category: '{category}', website: '{website}' }}"


def update_index_html(index_html_path, cooperatives):
    """Add new cooperatives to index.html."""
    with open(index_html_path, 'r') as f:
        content = f.read()

    # Find the cooperatives array - look for the closing bracket
    # The array is defined like: const cooperatives = [ ... ];
    pattern = r'(const cooperatives = \[)(.*?)(\];)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError("Could not find cooperatives array in index.html")

    array_start = match.group(1)
    array_content = match.group(2)
    array_end = match.group(3)

    # Generate new entries
    new_entries = [generate_coop_entry(coop) for coop in cooperatives]
    new_entries_str = ',\n'.join(new_entries)

    # Add new entries before the closing bracket
    # Strip trailing whitespace/commas from existing content
    array_content = array_content.rstrip().rstrip(',')

    updated_array = f"{array_start}{array_content},\n{new_entries_str}\n      {array_end}"

    # Replace in content
    new_content = re.sub(pattern, updated_array, content, flags=re.DOTALL)

    with open(index_html_path, 'w') as f:
        f.write(new_content)

    return len(cooperatives)


def main():
    parser = argparse.ArgumentParser(description='Import verified cooperatives to website')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported')
    parser.add_argument('--min-score', type=float, default=0.5, help='Minimum similarity score')
    args = parser.parse_args()

    print("Loading labeled data...")
    labeled_data = load_json(LABELED_DATA_PATH)

    # Get exportable cooperatives
    exportable = get_exportable_cooperatives(labeled_data, args.min_score)

    if not exportable:
        print(f"\nNo new cooperatives to export (min_score >= {args.min_score})")
        print("Run verify_candidates.py to verify more candidates first.")
        return

    print(f"\nFound {len(exportable)} cooperatives ready to export:")
    for coop in exportable:
        score = coop.get('similarity_score', 0)
        print(f"  - {coop['name']} ({coop['category']}) - score: {score:.3f}")

    if args.dry_run:
        print("\n[DRY RUN] No changes made.")
        return

    # Confirm
    confirm = input(f"\nProceed with importing {len(exportable)} cooperatives? [y/N]: ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    # Read current index.html to get max ID
    with open(INDEX_HTML_PATH, 'r') as f:
        index_content = f.read()
    current_max_id = get_current_max_id(index_content)
    print(f"\nCurrent max ID in website: {current_max_id}")

    # Update IDs to be sequential after current max
    for i, coop in enumerate(exportable):
        old_id = coop['id']
        new_id = current_max_id + i + 1
        coop['id'] = new_id
        print(f"  Reassigning ID: {old_id} -> {new_id}")

    # Capture screenshots
    print("\nCapturing screenshots...")
    successful = []
    for coop in exportable:
        print(f"  Capturing {coop['name']}...")
        if capture_screenshot(coop, SCREENSHOTS_DIR):
            successful.append(coop)
            print(f"    Done")
        else:
            print(f"    Failed - skipping")

    if not successful:
        print("\nNo screenshots captured successfully. Aborting import.")
        return

    # Update index.html
    print(f"\nUpdating index.html with {len(successful)} cooperatives...")
    count = update_index_html(INDEX_HTML_PATH, successful)
    print(f"  Added {count} entries")

    # Mark as exported in labeled_data
    exported_websites = {c['website'] for c in successful}
    for coop in labeled_data['verified_cooperatives']:
        if coop['website'] in exported_websites:
            coop['exported_to_website'] = True
            coop['export_date'] = datetime.now().isoformat()

    labeled_data['metadata']['last_updated'] = datetime.now().isoformat()
    save_json(labeled_data, LABELED_DATA_PATH)

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"Successfully imported: {len(successful)}")
    print(f"Failed: {len(exportable) - len(successful)}")
    print(f"\nScreenshots saved to: {SCREENSHOTS_DIR}")
    print(f"Updated: {INDEX_HTML_PATH}")
    print(f"\nDon't forget to commit and push your changes!")


if __name__ == '__main__':
    main()

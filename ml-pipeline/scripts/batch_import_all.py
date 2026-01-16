#!/usr/bin/env python3
"""
Batch import all verified cooperatives with websites into the website.

This script:
1. Reads cooperatives from verified_with_websites.json
2. Compares against existing cooperatives in index.html
3. Captures screenshots for new cooperatives using Puppeteer
4. Updates index.html with new cooperative entries

Usage:
    python batch_import_all.py [--dry-run] [--limit N]

Options:
    --dry-run       Show what would be imported without making changes
    --limit N       Only import N cooperatives (for testing)
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
VERIFIED_WITH_WEBSITES_PATH = DATA_DIR / "verified_with_websites.json"
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


def get_existing_websites(index_html_path):
    """Extract existing website URLs from index.html."""
    with open(index_html_path, 'r') as f:
        content = f.read()

    # Find all website values
    websites = set()
    matches = re.findall(r"website:\s*['\"]([^'\"]+)['\"]", content)
    for url in matches:
        # Normalize URL for comparison
        normalized = url.lower().rstrip('/')
        websites.add(normalized)

    return websites


def get_current_max_id(index_html_path):
    """Extract the current maximum ID from index.html."""
    with open(index_html_path, 'r') as f:
        content = f.read()

    id_matches = re.findall(r'\{\s*id:\s*(\d+)', content)
    if id_matches:
        return max(int(id) for id in id_matches)
    return 0


def capture_screenshot(coop, screenshots_dir):
    """Capture screenshot for a cooperative using Node.js script."""
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
        await new Promise(r => setTimeout(r, 2000));

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
            error_msg = result.stdout.strip() or result.stderr.strip()
            print(f"    Error: {error_msg[:80]}")
        return success
    except subprocess.TimeoutExpired:
        print(f"    Timeout")
        return False
    except Exception as e:
        print(f"    Exception: {e}")
        return False
    finally:
        temp_script.unlink(missing_ok=True)


def generate_coop_entry(coop):
    """Generate JavaScript object entry for a cooperative."""
    name = coop['name'].replace("'", "\\'").replace('"', '\\"')
    category = coop['category']
    website = coop['website']
    location = coop.get('location', 'Iowa')

    return f"            {{ id: {coop['id']}, name: '{name}', location: '{location}', type: '{category.title()}', website: '{website}', category: '{category}' }}"


def update_index_html(index_html_path, cooperatives):
    """Add new cooperatives to index.html."""
    with open(index_html_path, 'r') as f:
        content = f.read()

    # Find the cooperatives array
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
    array_content = array_content.rstrip().rstrip(',')

    updated_array = f"{array_start}{array_content},\n{new_entries_str}\n        {array_end}"

    new_content = re.sub(pattern, updated_array, content, flags=re.DOTALL)

    with open(index_html_path, 'w') as f:
        f.write(new_content)

    return len(cooperatives)


def main():
    parser = argparse.ArgumentParser(description='Import all verified cooperatives to website')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported')
    parser.add_argument('--limit', type=int, help='Limit number of imports')
    args = parser.parse_args()

    print("Loading data...")
    verified_data = load_json(VERIFIED_WITH_WEBSITES_PATH)
    all_coops = verified_data['cooperatives']

    # Get existing websites from index.html
    existing_websites = get_existing_websites(INDEX_HTML_PATH)
    print(f"Existing cooperatives on website: {len(existing_websites)}")

    # Filter to only new cooperatives
    new_coops = []
    for coop in all_coops:
        website = coop.get('website', '').lower().rstrip('/')
        if website and website not in existing_websites:
            new_coops.append(coop)

    print(f"New cooperatives to import: {len(new_coops)}")

    if not new_coops:
        print("\nNo new cooperatives to import.")
        return

    # Apply limit if specified
    if args.limit:
        new_coops = new_coops[:args.limit]
        print(f"Limited to: {len(new_coops)}")

    # Show what will be imported
    print("\nCooperatives to import:")
    for coop in new_coops[:20]:
        print(f"  - {coop['name']} ({coop['category']})")
    if len(new_coops) > 20:
        print(f"  ... and {len(new_coops) - 20} more")

    if args.dry_run:
        print("\n[DRY RUN] No changes made.")
        return

    # Confirm
    confirm = input(f"\nProceed with importing {len(new_coops)} cooperatives? [y/N]: ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    # Get current max ID
    current_max_id = get_current_max_id(INDEX_HTML_PATH)
    print(f"\nCurrent max ID: {current_max_id}")

    # Assign new IDs
    for i, coop in enumerate(new_coops):
        coop['id'] = current_max_id + i + 1

    # Capture screenshots
    print("\nCapturing screenshots...")
    successful = []
    failed = []

    for i, coop in enumerate(new_coops):
        print(f"  [{i+1}/{len(new_coops)}] {coop['name'][:40]}...", end=" ", flush=True)
        if capture_screenshot(coop, SCREENSHOTS_DIR):
            successful.append(coop)
            print("OK")
        else:
            failed.append(coop)
            print("FAILED")

    if not successful:
        print("\nNo screenshots captured successfully. Aborting import.")
        return

    # Update index.html
    print(f"\nUpdating index.html with {len(successful)} cooperatives...")
    count = update_index_html(INDEX_HTML_PATH, successful)
    print(f"  Added {count} entries")

    # Update labeled_data.json to mark as exported
    labeled_data = load_json(LABELED_DATA_PATH)
    exported_websites = {c['website'].lower().rstrip('/') for c in successful}

    for coop in labeled_data['verified_cooperatives']:
        website = coop.get('website', '').lower().rstrip('/')
        if website in exported_websites:
            coop['exported_to_website'] = True
            coop['export_date'] = datetime.now().isoformat()

    labeled_data['metadata']['last_updated'] = datetime.now().isoformat()
    save_json(labeled_data, LABELED_DATA_PATH)

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"Successfully imported: {len(successful)}")
    print(f"Failed (no screenshot): {len(failed)}")
    if failed:
        print("\nFailed cooperatives:")
        for coop in failed[:10]:
            print(f"  - {coop['name']}: {coop['website']}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")
    print(f"\nScreenshots saved to: {SCREENSHOTS_DIR}")
    print(f"Updated: {INDEX_HTML_PATH}")
    print(f"\nDon't forget to commit and push your changes!")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Verification CLI for manually reviewing candidate cooperatives.

This script presents candidates one at a time, sorted by similarity score,
allowing human reviewers to verify or reject them. Results are saved to
the labeled_data.json file for active learning.

Usage:
    python verify_candidates.py [--num N] [--min-score S]

Options:
    --num N         Number of candidates to review (default: 10)
    --min-score S   Minimum similarity score to consider (default: 0.4)
"""

import json
import argparse
import webbrowser
from datetime import datetime
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
LABELED_DATA_PATH = DATA_DIR / "labeled_data.json"
SIMILARITY_RESULTS_PATH = DATA_DIR / "similarity_results.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    """Save JSON file with pretty formatting."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_unreviewed_candidates(labeled_data, similarity_results, min_score=0.4):
    """Get candidates that haven't been reviewed yet, sorted by score."""
    # Get already reviewed websites
    reviewed_websites = set()
    for coop in labeled_data['verified_cooperatives']:
        reviewed_websites.add(coop['website'])
    for candidate in labeled_data['rejected_candidates']:
        reviewed_websites.add(candidate['website'])

    # Filter to unreviewed candidates with sufficient score
    unreviewed = []
    for candidate in similarity_results:
        if candidate['website'] not in reviewed_websites:
            score = candidate.get('cooperative_score', 0)
            if score >= min_score:
                unreviewed.append(candidate)

    # Sort by cooperative_score descending
    unreviewed.sort(key=lambda x: x.get('cooperative_score', 0), reverse=True)
    return unreviewed


def display_candidate(candidate, index, total):
    """Display candidate information for review."""
    print("\n" + "=" * 60)
    print(f"CANDIDATE {index + 1} of {total}")
    print("=" * 60)
    print(f"\nName:     {candidate['name']}")
    print(f"Website:  {candidate['website']}")
    print(f"Location: {candidate.get('location', 'Unknown')}")
    print(f"Source:   {candidate.get('source', 'Unknown')}")

    score = candidate.get('cooperative_score', 0)
    print(f"\nSimilarity Score: {score:.3f}")

    # Show most similar cooperatives
    if candidate.get('similarity_scores') and candidate['similarity_scores'].get('most_similar'):
        print("\nMost similar to:")
        for similar in candidate['similarity_scores']['most_similar'][:3]:
            print(f"  - {similar['name']} ({similar['category']}): {similar['similarity']:.3f}")

    # Show content preview
    preview = candidate.get('content_preview', '')
    if preview:
        print(f"\nContent preview:")
        print("-" * 40)
        # Truncate and clean up preview
        preview_lines = preview[:500].split('\n')
        for line in preview_lines[:8]:
            print(f"  {line.strip()}")
        if len(preview) > 500:
            print("  ...")

    print("\n" + "-" * 60)


def get_user_decision():
    """Get user's decision on the candidate."""
    while True:
        print("\nOptions:")
        print("  [y] Yes - This is a cooperative (add to verified)")
        print("  [n] No - This is NOT a cooperative (reject)")
        print("  [o] Open website in browser")
        print("  [s] Skip - Review later")
        print("  [q] Quit reviewing")

        choice = input("\nYour choice: ").strip().lower()

        if choice in ['y', 'n', 'o', 's', 'q']:
            return choice
        else:
            print("Invalid choice. Please enter y, n, o, s, or q.")


def determine_category(candidate):
    """Try to determine the category based on similarity matches."""
    if candidate.get('similarity_scores') and candidate['similarity_scores'].get('most_similar'):
        # Count categories from top matches
        category_counts = {}
        for similar in candidate['similarity_scores']['most_similar']:
            cat = similar.get('category', 'other')
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Return most common category
        if category_counts:
            return max(category_counts, key=category_counts.get)

    return 'other'


def update_stats(labeled_data, verified_count, rejected_count):
    """Update statistics in labeled data."""
    labeled_data['stats']['total_verified'] = len(labeled_data['verified_cooperatives'])
    labeled_data['stats']['total_rejected'] = len(labeled_data['rejected_candidates'])
    labeled_data['stats']['total_reviewed'] += verified_count + rejected_count

    # Calculate and record precision
    if verified_count + rejected_count > 0:
        precision = verified_count / (verified_count + rejected_count)
        labeled_data['stats']['precision_history'].append({
            'timestamp': datetime.now().isoformat(),
            'verified': verified_count,
            'rejected': rejected_count,
            'precision': precision,
            'cumulative_verified': labeled_data['stats']['total_verified'],
            'cumulative_reviewed': labeled_data['stats']['total_reviewed']
        })

    labeled_data['metadata']['last_updated'] = datetime.now().isoformat()


def main():
    parser = argparse.ArgumentParser(description='Review candidate cooperatives')
    parser.add_argument('--num', type=int, default=10, help='Number of candidates to review')
    parser.add_argument('--min-score', type=float, default=0.4, help='Minimum similarity score')
    args = parser.parse_args()

    # Load data
    print("Loading data...")
    labeled_data = load_json(LABELED_DATA_PATH)
    similarity_results = load_json(SIMILARITY_RESULTS_PATH)

    # Get unreviewed candidates
    candidates = get_unreviewed_candidates(labeled_data, similarity_results, args.min_score)

    if not candidates:
        print("\nNo unreviewed candidates found with score >= {:.2f}".format(args.min_score))
        print("Try lowering --min-score or running similarity_search.py with new candidates.")
        return

    num_to_review = min(args.num, len(candidates))
    print(f"\nFound {len(candidates)} unreviewed candidates (score >= {args.min_score})")
    print(f"Will review up to {num_to_review} candidates.\n")

    # Review loop
    verified_count = 0
    rejected_count = 0
    skipped_count = 0

    for i, candidate in enumerate(candidates[:num_to_review]):
        display_candidate(candidate, i, num_to_review)

        while True:
            decision = get_user_decision()

            if decision == 'o':
                # Open website in browser
                print(f"Opening {candidate['website']}...")
                webbrowser.open(candidate['website'])
                continue
            elif decision == 'y':
                # Add to verified cooperatives
                category = determine_category(candidate)
                print(f"\nInferred category: {category}")
                custom_cat = input("Press Enter to accept or type a different category: ").strip()
                if custom_cat:
                    category = custom_cat

                new_coop = {
                    'id': max(c['id'] for c in labeled_data['verified_cooperatives']) + 1,
                    'name': candidate['name'],
                    'category': category,
                    'website': candidate['website'],
                    'location': candidate.get('location', 'Iowa'),
                    'verified_date': datetime.now().isoformat(),
                    'source': 'ml_pipeline',
                    'similarity_score': candidate.get('cooperative_score', 0)
                }
                labeled_data['verified_cooperatives'].append(new_coop)
                verified_count += 1
                print(f"Added '{candidate['name']}' as verified cooperative (category: {category})")
                break
            elif decision == 'n':
                # Add to rejected
                rejected = {
                    'name': candidate['name'],
                    'website': candidate['website'],
                    'location': candidate.get('location', 'Unknown'),
                    'rejected_date': datetime.now().isoformat(),
                    'similarity_score': candidate.get('cooperative_score', 0),
                    'reason': 'not_cooperative'
                }
                labeled_data['rejected_candidates'].append(rejected)
                rejected_count += 1
                print(f"Rejected '{candidate['name']}'")
                break
            elif decision == 's':
                skipped_count += 1
                print("Skipped")
                break
            elif decision == 'q':
                print("\nQuitting review session...")
                break

        if decision == 'q':
            break

    # Update stats and save
    update_stats(labeled_data, verified_count, rejected_count)
    save_json(labeled_data, LABELED_DATA_PATH)

    # Print summary
    print("\n" + "=" * 60)
    print("REVIEW SESSION SUMMARY")
    print("=" * 60)
    print(f"Verified:  {verified_count}")
    print(f"Rejected:  {rejected_count}")
    print(f"Skipped:   {skipped_count}")

    if verified_count + rejected_count > 0:
        precision = verified_count / (verified_count + rejected_count)
        print(f"\nSession precision: {precision:.1%}")

    print(f"\nTotal verified cooperatives: {labeled_data['stats']['total_verified']}")
    print(f"Total rejected candidates:   {labeled_data['stats']['total_rejected']}")
    print(f"\nResults saved to {LABELED_DATA_PATH}")


if __name__ == '__main__':
    main()

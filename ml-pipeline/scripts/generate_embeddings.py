#!/usr/bin/env python3
"""
Generate embeddings for cooperative website content using sentence-transformers.
"""

import json
import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"
CONTENT_FILE = DATA_DIR / "cooperative_content.json"
EMBEDDINGS_FILE = MODELS_DIR / "cooperative_embeddings.pkl"

# Model configuration
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast and effective for similarity search
# Alternative: "all-mpnet-base-v2" for higher quality but slower


def create_text_for_embedding(coop: dict) -> str:
    """Create a combined text representation for embedding."""
    parts = []

    # Include name and type for context
    parts.append(f"{coop['name']} - {coop['type']}")
    parts.append(f"Location: {coop['location']}")

    # Main content
    if coop.get("content"):
        # Truncate very long content to avoid memory issues
        content = coop["content"][:10000]
        parts.append(content)

    return "\n\n".join(parts)


def main():
    """Generate embeddings for all cooperatives with content."""
    print("Loading scraped content...")
    with open(CONTENT_FILE) as f:
        cooperatives = json.load(f)

    # Filter to only those with content
    coops_with_content = [c for c in cooperatives if c.get("content")]
    print(f"Found {len(coops_with_content)} cooperatives with content")

    if not coops_with_content:
        print("No content to embed. Run scrape_websites.py first.")
        return

    # Load model
    print(f"\nLoading sentence-transformer model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # Prepare texts
    print("Preparing texts for embedding...")
    texts = [create_text_for_embedding(c) for c in coops_with_content]

    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} cooperatives...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True  # For cosine similarity
    )

    # Create output structure
    output = {
        "model_name": MODEL_NAME,
        "embedding_dim": embeddings.shape[1],
        "cooperatives": [],
        "embeddings": embeddings
    }

    for i, coop in enumerate(coops_with_content):
        output["cooperatives"].append({
            "id": coop["id"],
            "name": coop["name"],
            "website": coop["website"],
            "category": coop["category"],
            "type": coop["type"],
            "location": coop["location"],
            "embedding_index": i
        })

    # Save embeddings
    MODELS_DIR.mkdir(exist_ok=True)
    print(f"\nSaving embeddings to {EMBEDDINGS_FILE}")
    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(output, f)

    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Model: {MODEL_NAME}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"Total embeddings: {len(embeddings)}")
    print(f"Embeddings file size: {EMBEDDINGS_FILE.stat().st_size / 1024:.1f} KB")

    # Category breakdown
    print("\nEmbeddings by category:")
    categories = {}
    for c in coops_with_content:
        cat = c["category"]
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()

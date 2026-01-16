#!/usr/bin/env python3
"""
Similarity search for finding cooperative-like businesses.
Compares candidate websites against verified cooperative embeddings.
"""

import json
import pickle
from pathlib import Path

import numpy as np
import requests
import trafilatura
from sentence_transformers import SentenceTransformer

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"
EMBEDDINGS_FILE = MODELS_DIR / "cooperative_embeddings.pkl"
CANDIDATES_FILE = DATA_DIR / "candidates.json"
RESULTS_FILE = DATA_DIR / "similarity_results.json"

# Request settings
TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
HEADERS = {"User-Agent": USER_AGENT}


class CooperativeSimilaritySearch:
    """Search for businesses similar to verified cooperatives."""

    def __init__(self):
        self.embeddings_data = None
        self.model = None
        self.embeddings = None
        self.cooperatives = None

    def load(self):
        """Load embeddings and model."""
        print("Loading embeddings...")
        with open(EMBEDDINGS_FILE, "rb") as f:
            self.embeddings_data = pickle.load(f)

        self.embeddings = self.embeddings_data["embeddings"]
        self.cooperatives = self.embeddings_data["cooperatives"]

        print(f"Loading model: {self.embeddings_data['model_name']}")
        self.model = SentenceTransformer(self.embeddings_data["model_name"])

        print(f"Loaded {len(self.cooperatives)} cooperative embeddings")

    def fetch_and_extract(self, url: str) -> str | None:
        """Fetch URL and extract text content."""
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            text = trafilatura.extract(response.text, url=url)
            return text
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def create_embedding_text(self, name: str, location: str, content: str) -> str:
        """Create text for embedding."""
        parts = [f"{name}", f"Location: {location}"]
        if content:
            parts.append(content[:10000])
        return "\n\n".join(parts)

    def compute_similarity(self, candidate_embedding: np.ndarray) -> dict:
        """Compute similarity scores against all verified cooperatives."""
        # Cosine similarity (embeddings are normalized)
        similarities = np.dot(self.embeddings, candidate_embedding)

        # Overall score (mean of top-k similarities)
        top_k = 5
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return {
            "mean_similarity": float(np.mean(similarities)),
            "max_similarity": float(np.max(similarities)),
            "top_k_mean": float(np.mean(similarities[top_indices])),
            "most_similar": [
                {
                    "name": self.cooperatives[i]["name"],
                    "category": self.cooperatives[i]["category"],
                    "similarity": float(similarities[i])
                }
                for i in top_indices
            ]
        }

    def score_candidate(self, candidate: dict) -> dict:
        """Score a single candidate business."""
        result = {
            "name": candidate["name"],
            "website": candidate.get("website"),
            "location": candidate.get("location", "Iowa"),
            "source": candidate.get("source", "unknown"),
            "content_extracted": False,
            "similarity_scores": None,
            "cooperative_score": 0.0
        }

        # Fetch and extract content
        if candidate.get("website"):
            content = self.fetch_and_extract(candidate["website"])
            if content:
                result["content_extracted"] = True
                result["content_preview"] = content[:500] + "..." if len(content) > 500 else content

                # Generate embedding
                text = self.create_embedding_text(
                    candidate["name"],
                    candidate.get("location", "Iowa"),
                    content
                )
                embedding = self.model.encode(text, normalize_embeddings=True)

                # Compute similarities
                result["similarity_scores"] = self.compute_similarity(embedding)
                result["cooperative_score"] = result["similarity_scores"]["top_k_mean"]

        return result

    def score_candidates(self, candidates: list[dict]) -> list[dict]:
        """Score multiple candidates and rank by similarity."""
        results = []

        for i, candidate in enumerate(candidates):
            print(f"\n[{i+1}/{len(candidates)}] Scoring: {candidate['name']}")
            result = self.score_candidate(candidate)
            results.append(result)

            if result["content_extracted"]:
                print(f"  Cooperative score: {result['cooperative_score']:.3f}")
                if result["similarity_scores"]:
                    top_match = result["similarity_scores"]["most_similar"][0]
                    print(f"  Most similar to: {top_match['name']} ({top_match['similarity']:.3f})")
            else:
                print("  Could not extract content")

        # Sort by cooperative score
        results.sort(key=lambda x: x["cooperative_score"], reverse=True)

        return results


def main():
    """Run similarity search on candidate businesses."""
    # Check for candidates file
    if not CANDIDATES_FILE.exists():
        print(f"No candidates file found at {CANDIDATES_FILE}")
        print("\nCreating example candidates file...")

        # Create example candidates
        example_candidates = [
            {
                "name": "Example Farm Cooperative",
                "website": "https://example.com",
                "location": "Example City, IA",
                "source": "example"
            }
        ]
        with open(CANDIDATES_FILE, "w") as f:
            json.dump(example_candidates, f, indent=2)

        print(f"Created {CANDIDATES_FILE}")
        print("Add candidate businesses to this file and run again.")
        return

    # Load candidates
    print("Loading candidates...")
    with open(CANDIDATES_FILE) as f:
        candidates = json.load(f)

    print(f"Found {len(candidates)} candidates to score\n")

    # Initialize search
    search = CooperativeSimilaritySearch()
    search.load()

    # Score candidates
    print("\n" + "="*50)
    print("SCORING CANDIDATES")
    print("="*50)

    results = search.score_candidates(candidates)

    # Save results
    print(f"\nSaving results to {RESULTS_FILE}")
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print("\n" + "="*50)
    print("TOP CANDIDATES (by cooperative similarity)")
    print("="*50)

    for i, result in enumerate(results[:10]):
        score = result["cooperative_score"]
        name = result["name"]
        print(f"\n{i+1}. {name}")
        print(f"   Score: {score:.3f}")
        if result["similarity_scores"]:
            top = result["similarity_scores"]["most_similar"][0]
            print(f"   Most similar to: {top['name']} ({top['category']})")


if __name__ == "__main__":
    main()

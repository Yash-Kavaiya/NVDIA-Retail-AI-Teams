"""
Example: Basic image search by text query.

This example demonstrates how to search for images using text descriptions.
"""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import Config
from src.search_engine import ImageSearchEngine


async def main():
    """Run basic text search example."""
    print("=" * 80)
    print("EXAMPLE: Text-Based Image Search")
    print("=" * 80)
    
    # Load configuration
    config = Config.from_env()
    config.validate()
    
    # Initialize search engine
    print("\n✓ Initializing search engine...")
    engine = ImageSearchEngine(config)
    
    # Get collection stats
    stats = engine.get_collection_stats()
    print(f"✓ Connected to collection: {stats['collection_name']}")
    print(f"✓ Total images indexed: {stats['points_count']:,}")
    
    # Example queries
    queries = [
        "silver watch for women",
        "black casual shoes",
        "grey t-shirt for men",
        "blue handbag",
        "casual summer wear"
    ]
    
    print("\n" + "=" * 80)
    print("Running Example Queries")
    print("=" * 80)
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        
        results = await engine.search_by_text(query, limit=5, score_threshold=0.3)
        
        if results:
            print(f"✓ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.filename[:60]}")
                print(f"      Similarity: {result.score*100:.2f}%")
                print(f"      URL: {result.image_url[:70]}...")
        else:
            print("   ✗ No results found")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

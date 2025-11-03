"""
Example: Compare text search vs image search results.

This example demonstrates the difference between semantic text search
and visual similarity search.
"""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import Config
from src.search_engine import ImageSearchEngine


async def main():
    """Compare search methods."""
    print("=" * 80)
    print("EXAMPLE: Text Search vs Image Search Comparison")
    print("=" * 80)
    
    # Load configuration
    config = Config.from_env()
    engine = ImageSearchEngine(config)
    
    # Test case: Watch search
    text_query = "elegant silver watch for women"
    image_url = "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg"
    
    print(f"\n📝 Text Query: '{text_query}'")
    print(f"🖼️  Image Query: {image_url[:60]}...")
    
    print("\n" + "-" * 80)
    print("TEXT SEARCH RESULTS")
    print("-" * 80)
    
    text_results = await engine.search_by_text(text_query, limit=5)
    
    if text_results:
        for i, result in enumerate(text_results, 1):
            print(f"{i}. {result.filename[:60]}")
            print(f"   Score: {result.score*100:.2f}%")
    else:
        print("No results found")
    
    print("\n" + "-" * 80)
    print("IMAGE SEARCH RESULTS")
    print("-" * 80)
    
    image_results = await engine.search_by_image(image_url, limit=5)
    
    if image_results:
        for i, result in enumerate(image_results, 1):
            print(f"{i}. {result.filename[:60]}")
            print(f"   Score: {result.score*100:.2f}%")
    else:
        print("No results found")
    
    # Analyze overlap
    if text_results and image_results:
        text_ids = {r.id for r in text_results}
        image_ids = {r.id for r in image_results}
        overlap = len(text_ids & image_ids)
        
        print("\n" + "-" * 80)
        print("ANALYSIS")
        print("-" * 80)
        print(f"Overlapping results: {overlap}/5")
        print(f"Overlap percentage: {overlap/5*100:.1f}%")
        
        print("\n💡 Insights:")
        print("   • Text search finds semantically similar descriptions")
        print("   • Image search finds visually similar appearances")
        print("   • Overlap indicates both semantic and visual similarity")
        
        if overlap >= 3:
            print("   ✓ High overlap: Query and image are well-aligned")
        elif overlap >= 1:
            print("   ~ Moderate overlap: Some semantic/visual agreement")
        else:
            print("   ✗ Low overlap: Different semantic vs visual matches")


if __name__ == "__main__":
    asyncio.run(main())

"""
Example: Image similarity search.

This example shows how to find similar images using an image URL.
"""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import Config
from src.search_engine import ImageSearchEngine


async def main():
    """Run image similarity search example."""
    print("=" * 80)
    print("EXAMPLE: Image-to-Image Similarity Search")
    print("=" * 80)
    
    # Load configuration
    config = Config.from_env()
    config.validate()
    
    # Initialize search engine
    print("\n✓ Initializing search engine...")
    engine = ImageSearchEngine(config)
    
    # Example: Search for products similar to specific images
    test_images = {
        "Silver Watch": "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg",
        "Grey T-Shirt": "http://assets.myntassets.com/v1/images/style/properties/Puma-Men-Grey-T-shirt_32668f8a61454d0cc028a808cf21b383_images.jpg",
        "Black Watch": "http://assets.myntassets.com/v1/images/style/properties/Skagen-Men-Black-Watch_4982b2b1a76a85a85c9adc8b4b2d523a_images.jpg"
    }
    
    print("\n" + "=" * 80)
    print("Finding Similar Products")
    print("=" * 80)
    
    for description, image_url in test_images.items():
        print(f"\n🖼️  Query Image: {description}")
        print(f"   URL: {image_url[:70]}...")
        
        results = await engine.search_by_image(image_url, limit=5)
        
        if results:
            print(f"\n✓ Found {len(results)} similar products:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.filename[:60]}")
                print(f"      Visual Similarity: {result.score*100:.2f}%")
        else:
            print("   ✗ No similar products found")
        
        # Add small delay between requests
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)
    
    print("\n💡 Tip: Higher similarity scores indicate more visually similar products")
    print("💡 Tip: The same color, style, and category items score higher")


if __name__ == "__main__":
    asyncio.run(main())

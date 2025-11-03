"""
Example: Process a small sample of images.

This example shows how to process a small batch of images
to test the pipeline without processing the entire dataset.
"""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import Config
from src.pipeline import ImageEmbeddingPipeline


async def main():
    """Process sample images."""
    print("=" * 80)
    print("EXAMPLE: Processing Sample Images")
    print("=" * 80)
    
    # Load configuration
    config = Config.from_env()
    config.validate()
    
    print("\n✓ Configuration loaded")
    print(f"   NVIDIA API: {config.nvidia.embedding_url}")
    print(f"   Qdrant URL: {config.qdrant.url}")
    print(f"   Collection: {config.qdrant.collection_name}")
    print(f"   Batch size: {config.processing.batch_size}")
    
    # Initialize pipeline
    print("\n✓ Initializing pipeline...")
    pipeline = ImageEmbeddingPipeline(config)
    
    # Process sample (first 10 images)
    csv_file = "data/images.csv"
    
    print(f"\n📁 Processing {csv_file}")
    print(f"   Mode: Sample (first 10 images)")
    print()
    
    try:
        success, failure = await pipeline.process_csv(
            csv_file=csv_file,
            start_from=0,
            max_images=10
        )
        
        print("\n" + "=" * 80)
        print("Processing Summary")
        print("=" * 80)
        print(f"✓ Successfully processed: {success} images")
        print(f"✗ Failed: {failure} images")
        
        if success > 0:
            success_rate = (success / (success + failure)) * 100
            print(f"📊 Success rate: {success_rate:.1f}%")
        
        print("\n💡 Next steps:")
        print("   1. Run 'python tests/examples/basic_text_search.py' to search")
        print("   2. Process more images: python main.py 10 50")
        print("   3. Run full pipeline: python main.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure:")
        print("   1. NVIDIA API key is set in .env")
        print("   2. Qdrant is running on port 6333")
        print("   3. data/images.csv exists")


if __name__ == "__main__":
    asyncio.run(main())

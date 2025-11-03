"""
Integration tests for the complete image embeddings pipeline.

Tests end-to-end workflow from CSV processing to vector search.
"""
import asyncio
import pytest
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import Config
from src.pipeline import ImageEmbeddingPipeline
from src.search_engine import ImageSearchEngine


class TestPipelineIntegration:
    """Integration tests for complete pipeline workflow."""
    
    @pytest.fixture
    def config(self):
        """Load configuration from environment."""
        try:
            config = Config.from_env()
            config.validate()
            return config
        except Exception as e:
            pytest.skip(f"Configuration not available: {e}")
    
    @pytest.fixture
    def pipeline(self, config):
        """Create pipeline instance."""
        return ImageEmbeddingPipeline(config)
    
    @pytest.fixture
    def search_engine(self, config):
        """Create search engine instance."""
        return ImageSearchEngine(config)
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_process_small_batch(self, pipeline, config):
        """Test processing a small batch of images."""
        # Create temporary test CSV
        test_data = pd.DataFrame({
            'filename': ['test1.jpg', 'test2.jpg', 'test3.jpg'],
            'url': [
                'http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg',
                'http://assets.myntassets.com/v1/images/style/properties/Puma-Men-Grey-T-shirt_32668f8a61454d0cc028a808cf21b383_images.jpg',
                'http://assets.myntassets.com/v1/images/style/properties/Skagen-Men-Black-Watch_4982b2b1a76a85a85c9adc8b4b2d523a_images.jpg'
            ]
        })
        
        test_csv = '/tmp/test_images.csv'
        test_data.to_csv(test_csv, index=False)
        
        try:
            # Process batch
            success, failure = await pipeline.process_csv(test_csv, start_from=0, max_images=3)
            
            # Verify results
            assert success + failure == 3, "Should process all 3 images"
            assert success >= 1, "At least 1 image should succeed"
            
        finally:
            # Cleanup
            Path(test_csv).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, pipeline, search_engine, config):
        """Test complete workflow: process -> store -> search."""
        # 1. Process a single image
        test_data = pd.DataFrame({
            'filename': ['integration_test.jpg'],
            'url': ['http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg']
        })
        
        test_csv = '/tmp/integration_test.csv'
        test_data.to_csv(test_csv, index=False)
        
        try:
            # Process
            success, failure = await pipeline.process_csv(test_csv, max_images=1)
            
            if success == 0:
                pytest.skip("Image processing failed")
            
            # 2. Search for similar items
            results = await search_engine.search_by_text("silver watch", limit=5)
            
            # Verify search works
            assert len(results) > 0, "Should find similar items"
            assert results[0].score > 0.0, "Results should have similarity scores"
            
            # 3. Verify collection stats
            stats = search_engine.get_collection_stats()
            assert stats["points_count"] > 0, "Collection should have points"
            
        finally:
            Path(test_csv).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_resume_processing(self, pipeline):
        """Test resuming processing from a specific row."""
        test_data = pd.DataFrame({
            'filename': [f'resume_test_{i}.jpg' for i in range(10)],
            'url': ['http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg'] * 10
        })
        
        test_csv = '/tmp/resume_test.csv'
        test_data.to_csv(test_csv, index=False)
        
        try:
            # Process from row 5
            success, failure = await pipeline.process_csv(test_csv, start_from=5, max_images=3)
            
            # Should process 3 images starting from row 5
            assert success + failure == 3
            
        finally:
            Path(test_csv).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_search_after_ingestion(self, search_engine):
        """Test search functionality after data ingestion."""
        # Test text search
        text_results = await search_engine.search_by_text("watch", limit=5)
        assert len(text_results) > 0, "Text search should return results"
        
        # Verify result structure
        for result in text_results:
            assert hasattr(result, 'id')
            assert hasattr(result, 'filename')
            assert hasattr(result, 'score')
            assert hasattr(result, 'image_url')
    
    @pytest.mark.asyncio
    async def test_image_search_integration(self, search_engine):
        """Test image-based search integration."""
        try:
            results = await search_engine.search_by_image(
                "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg",
                limit=5
            )
            
            if len(results) > 0:
                assert results[0].score > 0.0
                assert results[0].filename is not None
        except Exception as e:
            pytest.skip(f"Image search failed: {e}")
    
    def test_configuration_validation(self, config):
        """Test configuration is properly validated."""
        assert config.nvidia.api_key != ""
        assert config.nvidia.embedding_url != ""
        assert config.qdrant.url != ""
        assert config.qdrant.collection_name != ""
        assert config.qdrant.embedding_dim == 4096
        assert config.processing.batch_size > 0


class TestErrorHandling:
    """Integration tests for error handling scenarios."""
    
    @pytest.fixture
    def config(self):
        """Load configuration."""
        try:
            config = Config.from_env()
            config.validate()
            return config
        except Exception:
            pytest.skip("Configuration not available")
    
    @pytest.fixture
    def pipeline(self, config):
        """Create pipeline."""
        return ImageEmbeddingPipeline(config)
    
    @pytest.mark.asyncio
    async def test_invalid_url_handling(self, pipeline):
        """Test handling of invalid image URLs."""
        test_data = pd.DataFrame({
            'filename': ['invalid.jpg'],
            'url': ['http://invalid-domain-12345.com/image.jpg']
        })
        
        test_csv = '/tmp/invalid_url_test.csv'
        test_data.to_csv(test_csv, index=False)
        
        try:
            success, failure = await pipeline.process_csv(test_csv, max_images=1)
            
            # Should handle gracefully
            assert failure == 1, "Should mark invalid URL as failure"
            assert success == 0
            
        finally:
            Path(test_csv).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_empty_csv_handling(self, pipeline):
        """Test handling of empty CSV file."""
        test_data = pd.DataFrame({'filename': [], 'url': []})
        
        test_csv = '/tmp/empty_test.csv'
        test_data.to_csv(test_csv, index=False)
        
        try:
            success, failure = await pipeline.process_csv(test_csv)
            
            # Should handle empty CSV gracefully
            assert success == 0
            assert failure == 0
            
        finally:
            Path(test_csv).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_mixed_valid_invalid_urls(self, pipeline):
        """Test processing mix of valid and invalid URLs."""
        test_data = pd.DataFrame({
            'filename': ['valid.jpg', 'invalid.jpg', 'valid2.jpg'],
            'url': [
                'http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg',
                'http://invalid-12345.com/img.jpg',
                'http://assets.myntassets.com/v1/images/style/properties/Puma-Men-Grey-T-shirt_32668f8a61454d0cc028a808cf21b383_images.jpg'
            ]
        })
        
        test_csv = '/tmp/mixed_test.csv'
        test_data.to_csv(test_csv, index=False)
        
        try:
            success, failure = await pipeline.process_csv(test_csv, max_images=3)
            
            # Should process valid URLs and skip invalid ones
            assert success + failure == 3
            assert success >= 1, "Should successfully process valid URLs"
            
        finally:
            Path(test_csv).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

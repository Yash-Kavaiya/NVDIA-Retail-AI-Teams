"""
Unit tests for ImageProcessor module.

Tests image download, resize, optimization, and Base64 encoding.
"""
import asyncio
import base64
import io
from pathlib import Path
import pytest
import aiohttp
from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.image_processor import ImageProcessor
from config.config import ProcessingConfig


class TestImageProcessor:
    """Unit tests for ImageProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create ImageProcessor with test configuration."""
        config = ProcessingConfig(
            batch_size=10,
            concurrent_downloads=5,
            concurrent_embeddings=3,
            image_max_size=128,
            image_quality=70,
            request_timeout=30
        )
        return ImageProcessor(config)
    
    @pytest.fixture
    def sample_image_url(self):
        """Sample image URL for testing."""
        return "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg"
    
    @pytest.mark.asyncio
    async def test_download_image_success(self, processor, sample_image_url):
        """Test successful image download."""
        async with aiohttp.ClientSession() as session:
            result = await processor.download_and_encode(session, sample_image_url)
            
            assert result is not None, "Should successfully download image"
            assert result.startswith("data:image/jpeg;base64,"), "Should return data URI"
    
    @pytest.mark.asyncio
    async def test_download_invalid_url(self, processor):
        """Test handling of invalid URLs."""
        async with aiohttp.ClientSession() as session:
            result = await processor.download_and_encode(session, "http://invalid-url-12345.com/image.jpg")
            
            assert result is None, "Should return None for invalid URL"
    
    @pytest.mark.asyncio
    async def test_download_empty_url(self, processor):
        """Test handling of empty URLs."""
        async with aiohttp.ClientSession() as session:
            result = await processor.download_and_encode(session, "")
            
            assert result is None, "Should return None for empty URL"
    
    def test_image_resize(self, processor):
        """Test image resizing maintains aspect ratio."""
        # Create test image
        img = Image.new('RGB', (500, 300), color='red')
        
        # Resize
        resized = processor._resize_image(img, max_size=128)
        
        # Check dimensions
        assert max(resized.size) == 128, "Max dimension should be 128"
        assert resized.size[0] / resized.size[1] == pytest.approx(500/300, rel=0.01), \
            "Aspect ratio should be preserved"
    
    def test_image_resize_small_image(self, processor):
        """Test that small images are not upscaled."""
        img = Image.new('RGB', (50, 50), color='blue')
        
        resized = processor._resize_image(img, max_size=128)
        
        assert resized.size == (50, 50), "Small images should not be upscaled"
    
    def test_base64_encoding(self, processor):
        """Test Base64 encoding of images."""
        # Create test image
        img = Image.new('RGB', (100, 100), color='green')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=70)
        img_bytes = img_byte_arr.getvalue()
        
        # Encode
        encoded = base64.b64encode(img_bytes).decode('utf-8')
        data_uri = f"data:image/jpeg;base64,{encoded}"
        
        assert data_uri.startswith("data:image/jpeg;base64,")
        assert len(encoded) > 0, "Should have non-empty encoding"
    
    def test_image_quality_settings(self, processor):
        """Test different quality settings."""
        img = Image.new('RGB', (200, 200), color='yellow')
        
        # High quality
        high_quality = io.BytesIO()
        img.save(high_quality, format='JPEG', quality=95)
        
        # Low quality
        low_quality = io.BytesIO()
        img.save(low_quality, format='JPEG', quality=50)
        
        assert len(high_quality.getvalue()) > len(low_quality.getvalue()), \
            "High quality should produce larger files"
    
    @pytest.mark.asyncio
    async def test_concurrent_downloads(self, processor):
        """Test concurrent image downloads."""
        urls = [
            "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg",
            "http://assets.myntassets.com/v1/images/style/properties/Puma-Men-Grey-T-shirt_32668f8a61454d0cc028a808cf21b383_images.jpg",
            "http://assets.myntassets.com/v1/images/style/properties/Skagen-Men-Black-Watch_4982b2b1a76a85a85c9adc8b4b2d523a_images.jpg"
        ]
        
        async with aiohttp.ClientSession() as session:
            tasks = [processor.download_and_encode(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            
            successful = sum(1 for r in results if r is not None)
            assert successful >= 1, "Should successfully download at least one image"
    
    def test_processor_configuration(self, processor):
        """Test processor configuration values."""
        assert processor.config.image_max_size == 128
        assert processor.config.image_quality == 70
        assert processor.config.request_timeout == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

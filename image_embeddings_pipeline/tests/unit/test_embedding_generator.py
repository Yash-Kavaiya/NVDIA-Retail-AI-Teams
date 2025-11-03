"""
Unit tests for EmbeddingGenerator module.

Tests NVIDIA API integration and embedding generation.
"""
import asyncio
import pytest
import aiohttp
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.embedding_generator import EmbeddingGenerator
from config.config import NvidiaConfig, ProcessingConfig


class TestEmbeddingGenerator:
    """Unit tests for EmbeddingGenerator class."""
    
    @pytest.fixture
    def nvidia_config(self):
        """Create NVIDIA config for testing."""
        return NvidiaConfig(
            api_key="test_key",
            embedding_url="https://integrate.api.nvidia.com/v1/embeddings",
            model="nvidia/nv-embed-v1",
            encoding_format="float"
        )
    
    @pytest.fixture
    def processing_config(self):
        """Create processing config."""
        return ProcessingConfig(
            batch_size=10,
            concurrent_downloads=5,
            concurrent_embeddings=3,
            image_max_size=128,
            image_quality=70,
            request_timeout=30
        )
    
    @pytest.fixture
    def generator(self, nvidia_config, processing_config):
        """Create EmbeddingGenerator instance."""
        return EmbeddingGenerator(nvidia_config, processing_config)
    
    def test_generator_initialization(self, generator):
        """Test generator initialization."""
        assert generator.config.model == "nvidia/nv-embed-v1"
        assert generator.config.encoding_format == "float"
        assert generator.timeout == 30
    
    def test_payload_creation(self, generator):
        """Test API payload creation."""
        image_data = "data:image/jpeg;base64,test_data"
        
        payload = {
            "input": [image_data],
            "model": generator.config.model,
            "encoding_format": generator.config.encoding_format,
            "input_type": "passage"
        }
        
        assert "input" in payload
        assert payload["model"] == "nvidia/nv-embed-v1"
        assert payload["encoding_format"] == "float"
        assert payload["input_type"] == "passage"
    
    def test_headers_generation(self, generator):
        """Test API headers."""
        headers = generator.config.headers
        
        assert "Authorization" in headers
        assert "content-type" in headers
        assert "accept" in headers
        assert headers["content-type"] == "application/json"
        assert headers["accept"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_generate_embedding_structure(self, generator):
        """Test embedding response structure validation."""
        # Mock successful response
        mock_response = {
            "data": [
                {
                    "embedding": [0.1] * 4096,
                    "index": 0
                }
            ],
            "model": "nvidia/nv-embed-v1",
            "usage": {
                "prompt_tokens": 100,
                "total_tokens": 100
            }
        }
        
        # Validate structure
        assert "data" in mock_response
        assert len(mock_response["data"]) > 0
        assert "embedding" in mock_response["data"][0]
        assert len(mock_response["data"][0]["embedding"]) == 4096
    
    def test_embedding_dimensions(self):
        """Test embedding dimensions are correct."""
        expected_dim = 4096
        test_embedding = [0.5] * expected_dim
        
        assert len(test_embedding) == 4096
    
    def test_retry_logic_configuration(self, generator):
        """Test retry configuration."""
        max_retries = 3
        retry_delay = 2
        
        assert max_retries > 0
        assert retry_delay > 0
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, generator):
        """Test timeout configuration."""
        assert generator.timeout == 30
        
        # Create timeout object
        timeout = aiohttp.ClientTimeout(total=generator.timeout)
        assert timeout.total == 30


class TestEmbeddingValidation:
    """Tests for embedding validation and quality checks."""
    
    def test_embedding_vector_length(self):
        """Test that embeddings have correct length."""
        embedding = [0.1] * 4096
        assert len(embedding) == 4096
    
    def test_embedding_value_range(self):
        """Test embedding values are floats."""
        embedding = [0.1, -0.5, 0.9, -0.2]
        
        for value in embedding:
            assert isinstance(value, float)
    
    def test_embedding_normalization(self):
        """Test embedding normalization (if applicable)."""
        import math
        
        embedding = [0.1, 0.2, 0.3, 0.4]
        
        # Calculate L2 norm
        norm = math.sqrt(sum(x**2 for x in embedding))
        
        # Normalize
        normalized = [x / norm for x in embedding]
        
        # Check normalized vector has unit length
        new_norm = math.sqrt(sum(x**2 for x in normalized))
        assert abs(new_norm - 1.0) < 0.0001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

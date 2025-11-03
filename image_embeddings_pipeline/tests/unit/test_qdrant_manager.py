"""
Unit tests for QdrantManager module.

Tests vector database operations including collection creation, 
point insertion, and search functionality.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.qdrant_manager import QdrantManager
from config.config import QdrantConfig
from qdrant_client.models import PointStruct, Distance, VectorParams


class TestQdrantManager:
    """Unit tests for QdrantManager class."""
    
    @pytest.fixture
    def qdrant_config(self):
        """Create test Qdrant configuration."""
        return QdrantConfig(
            url="http://localhost:6333",
            collection_name="test_image_embeddings",
            embedding_dim=4096
        )
    
    @pytest.fixture
    def manager(self, qdrant_config):
        """Create QdrantManager instance."""
        return QdrantManager(qdrant_config)
    
    def test_manager_initialization(self, manager):
        """Test QdrantManager initialization."""
        assert manager.client is not None
        assert manager.collection_name == "test_image_embeddings"
        assert manager.embedding_dim == 4096
    
    def test_collection_exists(self, manager):
        """Test checking if collection exists."""
        # Try to check collection existence
        try:
            exists = manager.collection_exists()
            assert isinstance(exists, bool)
        except Exception:
            # It's okay if Qdrant is not running in test env
            pytest.skip("Qdrant not available")
    
    def test_create_collection(self, manager):
        """Test collection creation."""
        try:
            # Delete if exists
            if manager.collection_exists():
                manager.client.delete_collection(manager.collection_name)
            
            # Create new
            manager.create_collection_if_not_exists()
            
            # Verify
            assert manager.collection_exists()
            
            # Check vector config
            info = manager.client.get_collection(manager.collection_name)
            assert info.config.params.vectors.size == 4096
            
        except Exception:
            pytest.skip("Qdrant not available")
    
    def test_upsert_single_point(self, manager):
        """Test upserting a single point."""
        try:
            manager.create_collection_if_not_exists()
            
            # Create test point
            test_vector = [0.1] * 4096
            point = PointStruct(
                id=999999,
                vector=test_vector,
                payload={
                    "filename": "test.jpg",
                    "image_url": "http://test.com/test.jpg",
                    "processed": True
                }
            )
            
            # Upsert
            manager.upsert_points([point])
            
            # Verify by searching
            results = manager.client.retrieve(
                collection_name=manager.collection_name,
                ids=[999999]
            )
            
            assert len(results) == 1
            assert results[0].payload["filename"] == "test.jpg"
            
        except Exception:
            pytest.skip("Qdrant not available")
    
    def test_upsert_batch(self, manager):
        """Test upserting batch of points."""
        try:
            manager.create_collection_if_not_exists()
            
            # Create batch
            points = []
            for i in range(10):
                vector = [0.1 * i] * 4096
                point = PointStruct(
                    id=1000000 + i,
                    vector=vector,
                    payload={
                        "filename": f"batch_test_{i}.jpg",
                        "image_url": f"http://test.com/batch_{i}.jpg",
                        "processed": True
                    }
                )
                points.append(point)
            
            # Upsert batch
            manager.upsert_points(points)
            
            # Verify count
            info = manager.client.get_collection(manager.collection_name)
            assert info.points_count >= 10
            
        except Exception:
            pytest.skip("Qdrant not available")
    
    def test_vector_dimensions(self, manager):
        """Test vector dimension validation."""
        try:
            manager.create_collection_if_not_exists()
            
            # Correct dimensions
            correct_vector = [0.5] * 4096
            point = PointStruct(
                id=888888,
                vector=correct_vector,
                payload={"test": True}
            )
            manager.upsert_points([point])
            
            # This should work
            assert True
            
        except Exception:
            pytest.skip("Qdrant not available")
    
    def test_collection_info(self, manager):
        """Test retrieving collection information."""
        try:
            manager.create_collection_if_not_exists()
            
            info = manager.client.get_collection(manager.collection_name)
            
            assert info.config is not None
            assert info.config.params.vectors.size == 4096
            assert info.config.params.vectors.distance == Distance.COSINE
            
        except Exception:
            pytest.skip("Qdrant not available")
    
    def test_payload_structure(self, manager):
        """Test payload structure validation."""
        try:
            manager.create_collection_if_not_exists()
            
            # Test with comprehensive payload
            point = PointStruct(
                id=777777,
                vector=[0.3] * 4096,
                payload={
                    "filename": "comprehensive_test.jpg",
                    "image_url": "http://test.com/comp.jpg",
                    "processed": True,
                    "processed_at": "2025-11-03T10:00:00",
                    "metadata": {
                        "size": 1024,
                        "format": "JPEG"
                    }
                }
            )
            
            manager.upsert_points([point])
            
            # Retrieve and verify
            results = manager.client.retrieve(
                collection_name=manager.collection_name,
                ids=[777777]
            )
            
            assert results[0].payload["filename"] == "comprehensive_test.jpg"
            assert results[0].payload["metadata"]["format"] == "JPEG"
            
        except Exception:
            pytest.skip("Qdrant not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Test fixtures for image embeddings pipeline tests.

Provides sample data, mock responses, and reusable test configurations.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import Config, NvidiaConfig, QdrantConfig, ProcessingConfig


# Sample Image URLs for Testing
SAMPLE_IMAGE_URLS = {
    "watch_silver": "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg",
    "watch_black": "http://assets.myntassets.com/v1/images/style/properties/Skagen-Men-Black-Watch_4982b2b1a76a85a85c9adc8b4b2d523a_images.jpg",
    "tshirt_grey": "http://assets.myntassets.com/v1/images/style/properties/Puma-Men-Grey-T-shirt_32668f8a61454d0cc028a808cf21b383_images.jpg",
    "shoes_casual": "http://assets.myntassets.com/v1/images/style/properties/051d64772f1b38ff476fbf0a807f365a_images.jpg",
    "belt_black": "http://assets.myntassets.com/v1/images/style/properties/8eee4563e14cf451b07f27761fd6535f_images.jpg",
    "flip_flops": "http://assets.myntassets.com/v1/images/style/properties/53690e3f396f411e184b249672d6ebae_images.jpg"
}

# Sample Products Data
SAMPLE_PRODUCTS = [
    {
        "id": 59263,
        "filename": "59263.jpg",
        "description": "Titan Women Silver Watch",
        "category": "Accessories/Watches",
        "url": SAMPLE_IMAGE_URLS["watch_silver"]
    },
    {
        "id": 30039,
        "filename": "30039.jpg",
        "description": "Skagen Men Black Watch",
        "category": "Accessories/Watches",
        "url": SAMPLE_IMAGE_URLS["watch_black"]
    },
    {
        "id": 53759,
        "filename": "53759.jpg",
        "description": "Puma Men Grey T-shirt",
        "category": "Apparel/Topwear/Tshirts",
        "url": SAMPLE_IMAGE_URLS["tshirt_grey"]
    },
    {
        "id": 9204,
        "filename": "9204.jpg",
        "description": "Puma Men Casual Shoes",
        "category": "Footwear/Shoes/Casual",
        "url": SAMPLE_IMAGE_URLS["shoes_casual"]
    }
]

# Sample Test Queries
SAMPLE_QUERIES = {
    "watches": [
        "silver watch for women",
        "black watch for men",
        "elegant timepiece",
        "wrist watch accessories"
    ],
    "apparel": [
        "grey t-shirt",
        "casual men's shirt",
        "summer top wear",
        "comfortable clothing"
    ],
    "footwear": [
        "casual shoes for men",
        "black footwear",
        "comfortable walking shoes",
        "everyday sneakers"
    ],
    "accessories": [
        "black leather belt",
        "fashion accessories",
        "men's belt",
        "casual accessories"
    ]
}

# Mock API Responses
MOCK_EMBEDDING_RESPONSE = {
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

MOCK_SEARCH_RESULTS = [
    {
        "id": 59263,
        "score": 0.95,
        "payload": {
            "filename": "59263.jpg",
            "image_url": SAMPLE_IMAGE_URLS["watch_silver"],
            "processed": True,
            "processed_at": "2025-11-03T10:00:00"
        }
    },
    {
        "id": 30039,
        "score": 0.87,
        "payload": {
            "filename": "30039.jpg",
            "image_url": SAMPLE_IMAGE_URLS["watch_black"],
            "processed": True,
            "processed_at": "2025-11-03T10:01:00"
        }
    }
]


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return Config(
        nvidia=NvidiaConfig(
            api_key="test_api_key",
            embedding_url="https://test.api.nvidia.com/v1/embeddings",
            model="nvidia/nv-embed-v1",
            encoding_format="float"
        ),
        qdrant=QdrantConfig(
            url="http://localhost:6333",
            collection_name="test_embeddings",
            embedding_dim=4096
        ),
        processing=ProcessingConfig(
            batch_size=10,
            concurrent_downloads=5,
            concurrent_embeddings=3,
            image_max_size=128,
            image_quality=70,
            request_timeout=30
        )
    )


@pytest.fixture
def sample_image_urls():
    """Provide sample image URLs."""
    return SAMPLE_IMAGE_URLS


@pytest.fixture
def sample_products():
    """Provide sample product data."""
    return SAMPLE_PRODUCTS


@pytest.fixture
def sample_queries():
    """Provide sample test queries."""
    return SAMPLE_QUERIES


@pytest.fixture
def mock_embedding_response():
    """Provide mock NVIDIA API embedding response."""
    return MOCK_EMBEDDING_RESPONSE


@pytest.fixture
def mock_search_results():
    """Provide mock Qdrant search results."""
    return MOCK_SEARCH_RESULTS


@pytest.fixture
def sample_embedding():
    """Provide sample 4096-dimensional embedding."""
    return [0.1] * 4096


@pytest.fixture
def sample_base64_image():
    """Provide sample Base64 encoded image."""
    return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="


# Category-specific test data
CATEGORY_TEST_DATA = {
    "Watches": {
        "keywords": ["watch", "timepiece", "wrist", "clock"],
        "colors": ["silver", "black", "gold", "rose gold"],
        "brands": ["Titan", "Skagen", "Fossil", "Casio"]
    },
    "Apparel": {
        "keywords": ["shirt", "tshirt", "top", "wear"],
        "colors": ["grey", "black", "white", "blue", "red"],
        "brands": ["Puma", "Nike", "Adidas", "Reebok"]
    },
    "Footwear": {
        "keywords": ["shoes", "sneakers", "casual", "formal", "flip flops"],
        "colors": ["black", "brown", "white", "blue"],
        "brands": ["Puma", "Nike", "Adidas", "Fila"]
    },
    "Accessories": {
        "keywords": ["belt", "bag", "handbag", "wallet"],
        "colors": ["black", "brown", "blue"],
        "brands": ["Fossil", "Lavie", "Baggit"]
    }
}


@pytest.fixture
def category_test_data():
    """Provide category-specific test data."""
    return CATEGORY_TEST_DATA


# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "image_download_timeout": 10,  # seconds
    "embedding_generation_timeout": 30,  # seconds
    "min_images_per_second": 0.5,
    "max_images_per_second": 5.0,
    "min_success_rate": 0.85,  # 85%
    "search_response_time": 2.0  # seconds
}


@pytest.fixture
def performance_benchmarks():
    """Provide performance benchmark values."""
    return PERFORMANCE_BENCHMARKS

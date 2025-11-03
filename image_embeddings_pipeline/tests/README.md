# 🧪 Tests & Examples

Comprehensive test suite and example scripts for the Image Embeddings Pipeline.

## 📁 Test Structure

```
tests/
├── unit/                          # Unit tests for individual components
│   ├── test_image_processor.py    # Image download, resize, encoding tests
│   ├── test_embedding_generator.py # NVIDIA API integration tests
│   └── test_qdrant_manager.py     # Vector database operation tests
│
├── integration/                   # End-to-end integration tests
│   └── test_pipeline_integration.py # Complete workflow tests
│
├── examples/                      # Practical usage examples
│   ├── basic_text_search.py       # Text-based image search
│   ├── image_similarity_search.py # Image-to-image search
│   ├── process_sample.py          # Process sample images
│   └── compare_search_methods.py  # Compare search approaches
│
├── fixtures/                      # Test data and configurations
│   └── test_fixtures.py           # Reusable test fixtures
│
├── test_search.py                 # Fashion search tests (26 test cases)
├── test_fashion_image_search.py   # Visual similarity tests (12 test cases)
└── pytest.ini                     # Pytest configuration
```

---

## 🚀 Quick Start

### Run All Tests

```bash
cd image_embeddings_pipeline
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Search functionality tests
pytest tests/test_search.py -v

# Visual similarity tests
pytest tests/test_fashion_image_search.py -v
```

### Run Tests by Marker

```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# API-dependent tests
pytest -m api

# Qdrant-dependent tests
pytest -m qdrant
```

---

## 📋 Test Categories

### Unit Tests (tests/unit/)

Test individual components in isolation.

#### `test_image_processor.py`
- ✅ Image download from URLs
- ✅ Image resizing with aspect ratio preservation
- ✅ Base64 encoding
- ✅ Quality optimization
- ✅ Error handling for invalid URLs
- ✅ Concurrent download operations

**Run:**
```bash
pytest tests/unit/test_image_processor.py -v
```

#### `test_embedding_generator.py`
- ✅ NVIDIA API request formatting
- ✅ Embedding response parsing
- ✅ Vector dimension validation (4096-dim)
- ✅ Timeout configuration
- ✅ Retry logic

**Run:**
```bash
pytest tests/unit/test_embedding_generator.py -v
```

#### `test_qdrant_manager.py`
- ✅ Collection creation and management
- ✅ Point insertion (single and batch)
- ✅ Vector dimension validation
- ✅ Payload structure validation
- ✅ Collection statistics retrieval

**Run:**
```bash
pytest tests/unit/test_qdrant_manager.py -v
```

---

### Integration Tests (tests/integration/)

Test complete workflows and system integration.

#### `test_pipeline_integration.py`
- ✅ End-to-end CSV processing
- ✅ Process → Store → Search workflow
- ✅ Resume processing from specific row
- ✅ Error handling (invalid URLs, empty CSVs)
- ✅ Mixed valid/invalid URL processing
- ✅ Configuration validation

**Run:**
```bash
pytest tests/integration/ -v
```

**Note:** Integration tests may take several minutes as they process real images.

---

### Search Tests

#### `test_search.py` - Fashion Search (26 Test Cases)

Comprehensive semantic search testing across categories:

**Category-Based Tests (Tests 1-9):**
- Men's shirts, women's dresses, bottomwear
- T-shirts, watches, handbags, belts
- Casual shoes, flip flops

**Color-Based Tests (Tests 10-12):**
- Black, grey, blue clothing items

**Season-Based Tests (Tests 13-14):**
- Summer wear, winter accessories

**Style/Occasion Tests (Tests 15-16):**
- Casual wear, ethnic wear

**Brand-Specific Tests (Tests 17-18):**
- Puma, Titan, Skagen, Fossil, Fabindia

**Gender-Specific Tests (Tests 19-21):**
- Men's, women's, boys' items

**Semantic Similarity Tests (Tests 22-23):**
- Query variation analysis

**Complex Queries (Tests 24-25):**
- Multi-attribute search
- Outfit combinations

**Statistics (Test 26):**
- Collection information and metrics

**Run:**
```bash
pytest tests/test_search.py -v

# Run all example queries (30+ queries)
python tests/test_search.py
```

---

#### `test_fashion_image_search.py` - Visual Similarity (12 Test Cases)

Image-to-image similarity testing:

**Watch Similarity (Tests 1-3):**
- Silver watch similarity
- Black watch similarity
- Cross-watch comparison

**Apparel Similarity (Test 4):**
- T-shirt visual matching

**Accessory Similarity (Test 5):**
- Belt and accessory matching

**Footwear Similarity (Tests 6-7):**
- Casual shoes, flip flops

**Visual Analysis (Tests 8-9):**
- Color-based similarity
- Category consistency

**Hybrid Search (Test 10):**
- Image vs text search comparison

**Discovery (Test 11):**
- Unknown product categorization

**Performance (Test 12):**
- Batch image search benchmarking

**Run:**
```bash
pytest tests/test_fashion_image_search.py -v

# Run visual similarity showcase
python tests/test_fashion_image_search.py
```

---

## 💡 Examples

Practical scripts demonstrating common use cases.

### 1. Basic Text Search

Search for products using text descriptions.

```bash
python tests/examples/basic_text_search.py
```

**Queries:**
- "silver watch for women"
- "black casual shoes"
- "grey t-shirt for men"
- "blue handbag"
- "casual summer wear"

---

### 2. Image Similarity Search

Find visually similar products using image URLs.

```bash
python tests/examples/image_similarity_search.py
```

**Test Cases:**
- Silver watch → Similar watches
- Grey t-shirt → Similar apparel
- Black watch → Similar accessories

---

### 3. Process Sample Images

Test the pipeline with a small batch (10 images).

```bash
python tests/examples/process_sample.py
```

**What it does:**
- Validates configuration
- Processes first 10 images from CSV
- Shows success/failure statistics
- Provides next steps guidance

---

### 4. Compare Search Methods

Compare text-based vs image-based search results.

```bash
python tests/examples/compare_search_methods.py
```

**Demonstrates:**
- Semantic text search results
- Visual image search results
- Overlap analysis
- Search method insights

---

## 🔧 Configuration

### pytest.ini

The test suite uses pytest markers for organized testing:

```ini
[tool:pytest]
markers =
    unit: Unit tests for individual components
    integration: Integration tests for complete workflows
    slow: Tests that take more than 5 seconds
    api: Tests that require NVIDIA API access
    qdrant: Tests that require Qdrant database
    network: Tests that require network access
    search: Search functionality tests
    pipeline: Pipeline processing tests
```

### Running Specific Markers

```bash
# Fast tests only
pytest -m "not slow"

# Tests requiring external services
pytest -m "api or qdrant"

# Search-related tests
pytest -m search
```

---

## 📊 Test Coverage

### Current Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `image_processor.py` | 10 tests | Unit tests |
| `embedding_generator.py` | 8 tests | Unit tests |
| `qdrant_manager.py` | 8 tests | Unit tests |
| `search_engine.py` | 26 tests | Text search |
| `pipeline.py` | 12 tests | Image search |
| Integration | 6 tests | E2E workflows |
| **Total** | **70+ tests** | Comprehensive |

---

## 🎯 Test Fixtures

Reusable test data in `tests/fixtures/test_fixtures.py`:

### Sample Data

```python
from tests.fixtures.test_fixtures import (
    SAMPLE_IMAGE_URLS,      # Pre-validated image URLs
    SAMPLE_PRODUCTS,        # Product metadata
    SAMPLE_QUERIES,         # Test queries by category
    CATEGORY_TEST_DATA,     # Keywords, colors, brands
    PERFORMANCE_BENCHMARKS  # Expected performance metrics
)
```

### Using Fixtures

```python
def test_with_fixture(sample_image_urls):
    url = sample_image_urls["watch_silver"]
    # Test with validated URL
```

---

## 🔍 Testing Best Practices

### 1. Before Running Tests

Ensure required services are running:

```bash
# Check Qdrant
curl http://localhost:6333/

# Verify environment variables
cat .env | grep -E "NVIDIA_API_KEY|QDRANT_URL"
```

### 2. Running Tests Safely

```bash
# Use test collection name to avoid data conflicts
export COLLECTION_NAME=test_image_embeddings

# Run tests
pytest tests/ -v
```

### 3. Skip Tests Without Dependencies

Tests automatically skip if services are unavailable:

```python
try:
    # Test requiring Qdrant
except Exception:
    pytest.skip("Qdrant not available")
```

### 4. Debugging Failed Tests

```bash
# Verbose output with full tracebacks
pytest tests/ -vv --tb=long

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s
```

---

## 📈 Performance Testing

### Benchmarks

Integration tests validate performance against benchmarks:

- **Image Download:** < 10 seconds per image
- **Embedding Generation:** < 30 seconds per image
- **Processing Speed:** 0.5 - 5.0 images/second
- **Success Rate:** ≥ 85%
- **Search Response:** < 2 seconds

### Run Performance Tests

```bash
pytest tests/integration/ -v -m slow
```

---

## 🐛 Troubleshooting Tests

### Common Issues

#### 1. NVIDIA API Errors
```
Error: 401 Unauthorized
```
**Solution:** Check `NVIDIA_API_KEY` in `.env`

#### 2. Qdrant Connection Failed
```
Error: Connection refused
```
**Solution:** Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`

#### 3. Import Errors
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Run from project root: `cd image_embeddings_pipeline`

#### 4. Slow Tests
```
Tests taking too long
```
**Solution:** Skip slow tests: `pytest -m "not slow"`

---

## 📚 Additional Resources

### Writing New Tests

1. **Unit Test Template:**
```python
import pytest
from src.module import Component

class TestComponent:
    @pytest.fixture
    def component(self):
        return Component()
    
    def test_functionality(self, component):
        result = component.method()
        assert result == expected
```

2. **Integration Test Template:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_workflow(config):
    # Setup
    pipeline = Pipeline(config)
    
    # Execute
    result = await pipeline.process()
    
    # Verify
    assert result.success > 0
```

### Test Naming Conventions

- `test_*.py` - Test files
- `Test*` - Test classes
- `test_*` - Test functions
- `test_*_success` - Success scenarios
- `test_*_error` - Error handling
- `test_*_integration` - Integration tests

---

## 🎓 Learning Path

### Beginner

1. Run example scripts in `tests/examples/`
2. Read test code to understand usage patterns
3. Run unit tests: `pytest tests/unit/ -v`

### Intermediate

1. Run integration tests: `pytest tests/integration/ -v`
2. Run search tests: `pytest tests/test_search.py -v`
3. Modify example scripts for your use case

### Advanced

1. Write custom tests for new features
2. Add performance benchmarks
3. Contribute test coverage improvements

---

## 🤝 Contributing Tests

When adding new tests:

1. ✅ Follow existing test structure
2. ✅ Use appropriate markers (`@pytest.mark.unit`, etc.)
3. ✅ Add fixtures for reusable data
4. ✅ Include docstrings explaining test purpose
5. ✅ Handle service unavailability gracefully
6. ✅ Update this README with new test descriptions

---

## 📄 Summary

- **70+ comprehensive tests** covering all components
- **Unit, integration, and functional tests**
- **26 fashion search test cases**
- **12 visual similarity test cases**
- **4 practical example scripts**
- **Reusable fixtures and configuration**
- **Performance benchmarking**
- **Clear documentation and best practices**

---

<div align="center">

**Happy Testing! 🧪**

For questions or issues, check the [main README](../README.md) or open an issue.

</div>

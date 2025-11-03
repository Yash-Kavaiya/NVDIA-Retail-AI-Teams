# 🖼️ Image Embeddings Pipeline

A high-performance, production-ready pipeline for processing fashion product images and generating multimodal embeddings using **NVIDIA NIM APIs**. This system enables semantic image search, visual similarity detection, and cross-modal retrieval (text-to-image and image-to-image search).

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20API-76B900.svg)](https://www.nvidia.com/)
[![Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-DC244C.svg)](https://qdrant.tech/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

This pipeline transforms raw product images into searchable vector embeddings, enabling:

- **Visual Similarity Search**: Find products that *look* similar, not just match in text
- **Multimodal Retrieval**: Search images using text descriptions or other images
- **Scalable Processing**: Concurrent downloads and embedding generation with async/await
- **Production-Ready**: Resumable processing, batch uploads, and comprehensive error handling
- **Retail AI**: Purpose-built for fashion/retail product catalogs

### Key Features

✨ **Multimodal Embeddings** - NVIDIA nv-embed-v1 (4096-dimensional vectors)  
🚀 **Async Processing** - Concurrent image downloads and API calls  
💾 **Vector Storage** - Qdrant database for efficient similarity search  
🔄 **Resumable Pipeline** - Continue processing from any row  
📊 **Rich Monitoring** - Progress bars, ETAs, and detailed statistics  
🎨 **Visual Search** - Find similar products by image or text query  

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
  - [Processing Images](#1-processing-images-from-csv)
  - [Resuming Jobs](#2-resuming-processing)
  - [Image Search](#3-searching-for-similar-images)
  - [Text Search](#4-text-based-image-search)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [API Reference](#-api-reference)

## 🏗️ Architecture

```
┌─────────────────┐
│   CSV File      │  (44K+ image URLs)
│  images.csv     │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────────────────┐
│         Image Embedding Pipeline                │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Download   │→│   Resize &   │            │
│  │    Images    │  │   Optimize   │            │
│  └──────────────┘  └──────┬───────┘            │
│                            │                     │
│                            v                     │
│                   ┌────────────────┐            │
│                   │ Base64 Encode  │            │
│                   └────────┬───────┘            │
│                            │                     │
│                            v                     │
│         ┌──────────────────────────────┐        │
│         │   NVIDIA NIM Embedding API   │        │
│         │   (nv-embed-v1: 4096-dim)    │        │
│         └──────────────┬───────────────┘        │
│                        │                         │
│                        v                         │
│              ┌─────────────────┐                │
│              │  Batch Upsert   │                │
│              │  (25 vectors)   │                │
│              └─────────┬───────┘                │
└──────────────────────────┼─────────────────────┘
                           │
                           v
                  ┌─────────────────┐
                  │  Qdrant Vector  │
                  │    Database     │
                  │  (44K vectors)  │
                  └─────────────────┘
                           │
                           v
                  ┌─────────────────┐
                  │  Search Engine  │
                  │  • Text → Image │
                  │  • Image → Image│
                  │  • Filters      │
                  └─────────────────┘
```

### Pipeline Flow

1. **Image Ingestion**: Read CSV with product image URLs
2. **Concurrent Download**: Fetch images with configurable concurrency (10 workers)
3. **Image Processing**: Resize to 128px, optimize quality (70%), Base64 encode
4. **Embedding Generation**: Call NVIDIA API with concurrent request handling (5 workers)
5. **Batch Upload**: Insert vectors to Qdrant in batches of 25
6. **Search & Retrieval**: Query by text or image for visual similarity

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- NVIDIA API key ([Get one here](https://build.nvidia.com/))
- Qdrant (local or cloud instance)

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd image_embeddings_pipeline
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Start Qdrant** (if running locally):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY="nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=image_embeddings

# Processing Configuration
BATCH_SIZE=25                  # Vectors per batch upload
EMBEDDING_DIM=4096             # NVIDIA nv-embed-v1 dimension
CONCURRENT_DOWNLOADS=10        # Parallel image downloads
CONCURRENT_EMBEDDINGS=5        # Parallel API requests
IMAGE_MAX_SIZE=128             # Max image dimension (px)
IMAGE_QUALITY=70               # JPEG quality (0-100)
REQUEST_TIMEOUT=60             # API timeout (seconds)
```

### Configuration Details

| Parameter | Default | Description |
|-----------|---------|-------------|
| `BATCH_SIZE` | 25 | Number of vectors to upload per batch |
| `CONCURRENT_DOWNLOADS` | 10 | Maximum parallel image downloads |
| `CONCURRENT_EMBEDDINGS` | 5 | Maximum concurrent API calls |
| `IMAGE_MAX_SIZE` | 128 | Maximum image dimension (maintains aspect ratio) |
| `IMAGE_QUALITY` | 70 | JPEG compression quality |
| `REQUEST_TIMEOUT` | 60 | HTTP request timeout in seconds |

---

## 📖 Usage

### 1. Processing Images from CSV

Process all images in your CSV file:

```bash
cd image_embeddings_pipeline
python main.py
```

**Expected Output**:
```
================================================================================
Starting processing at 2025-11-03 10:30:00
Concurrent downloads: 10
Concurrent embeddings: 5
Batch size: 25
================================================================================

[████████████████████████████████████████] 1000/1000 (100.0%) | ✓ 950 ✗ 50 | ETA: 0:00:00

================================================================================
Processing Complete!
================================================================================
✓ Successfully processed: 950 images
✗ Failed: 50 images
📊 Success rate: 95.0%
⏱️  Total time: 0:12:30
⚡ Average time per image: 0.75s
🚀 Processing speed: 1.33 images/second
💾 Collection: 'image_embeddings'
📐 Embedding dimension: 4096
================================================================================
```

### 2. Resuming Processing

If processing is interrupted, resume from a specific row:

```bash
# Resume from row 1000
python main.py 1000

# Resume from row 1000 and process only 500 images
python main.py 1000 500

# Process custom CSV file
python main.py 0 1000 data/custom_images.csv
```

### 3. Searching for Similar Images

Use the search engine to find visually similar products:

```python
import asyncio
from config.config import Config
from src.search_engine import ImageSearchEngine

async def search_similar_images():
    # Initialize
    config = Config.from_env()
    engine = ImageSearchEngine(config)
    
    # Search by image URL
    results = await engine.search_by_image(
        "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg",
        limit=10
    )
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.filename} (similarity: {result.score*100:.2f}%)")

asyncio.run(search_similar_images())
```

### 4. Text-Based Image Search

Search for images using natural language descriptions:

```python
async def search_by_text():
    config = Config.from_env()
    engine = ImageSearchEngine(config)
    
    # Search using text query
    results = await engine.search_by_text(
        "silver watch for women",
        limit=10,
        score_threshold=0.5  # Minimum similarity score
    )
    
    for result in results:
        print(f"• {result.filename} - {result.score*100:.1f}% match")
        print(f"  URL: {result.image_url}")

asyncio.run(search_by_text())
```

### 5. Advanced Search with Filters

Combine semantic search with metadata filters:

```python
async def advanced_search():
    config = Config.from_env()
    engine = ImageSearchEngine(config)
    
    results = await engine.search_with_filters(
        query="black casual shoes",
        filename_pattern="*.jpg",
        limit=10
    )
    
    for result in results:
        print(f"{result.filename}: {result.score*100:.2f}%")

asyncio.run(advanced_search())
```

---

## 🧪 Testing

The pipeline includes comprehensive test suites for validation.

### Run All Tests

```bash
cd image_embeddings_pipeline
pytest tests/ -v
```

### Run Specific Test Suite

```bash
# Fashion image search tests
pytest tests/test_fashion_image_search.py -v

# Basic search functionality
pytest tests/test_search.py -v
```

### Visual Similarity Showcase

Run the interactive visual similarity demo:

```bash
python tests/test_fashion_image_search.py
```

This will:
- Test visual similarity across product categories (watches, apparel, footwear)
- Compare image search vs. text search results
- Analyze color-based visual clustering
- Measure search performance metrics

**Sample Test Output**:
```
================================================================================
TEST 1: Image Similarity Search
Query Image: Titan Women Silver Watch
================================================================================

Top 10 Similar Products
┌──────┬────────────┬─────────────────────────────────────────────────────────┐
│ Rank │ Similarity │ Product                                                 │
├──────┼────────────┼─────────────────────────────────────────────────────────┤
│ #1   │ 98.45%     │ 59263.jpg                                               │
│ #2   │ 87.23%     │ Titan-Silver-Women-Watch-45678.jpg                      │
│ #3   │ 82.56%     │ Watch-Silver-Elegant-23456.jpg                          │
└──────┴────────────┴─────────────────────────────────────────────────────────┘

✓ Found 8/10 watch items
```

---

## 📁 Project Structure

```
image_embeddings_pipeline/
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── README.md                    # This file
│
├── config/
│   ├── __init__.py
│   └── config.py                # Configuration management
│
├── src/
│   ├── __init__.py
│   ├── pipeline.py              # Main processing pipeline
│   ├── image_processor.py       # Image download & encoding
│   ├── embedding_generator.py   # NVIDIA API integration
│   ├── qdrant_manager.py        # Vector database operations
│   └── search_engine.py         # Search functionality
│
├── tests/
│   ├── __init__.py
│   ├── test_search.py           # Basic search tests
│   └── test_fashion_image_search.py  # Visual similarity tests
│
├── data/
│   └── images.csv               # Product image URLs (44K+ rows)
│
└── logs/
    └── pipeline.log             # Processing logs
```

---

## ⚡ Performance

### Benchmarks

Tested on a standard development machine with good internet connection:

| Metric | Value |
|--------|-------|
| **Processing Speed** | ~1.3 images/second |
| **Average Latency** | 0.75s per image |
| **Concurrent Downloads** | 10 workers |
| **Concurrent API Calls** | 5 workers |
| **Batch Upload Size** | 25 vectors |
| **Success Rate** | ~95% |

### Processing 10,000 Images

- **Total Time**: ~2 hours
- **Success**: ~9,500 images
- **Failures**: ~500 images (network errors, invalid URLs)
- **Storage**: ~160MB in Qdrant (4096-dim float vectors)

### Optimization Tips

1. **Increase Concurrency**: For faster networks
   ```bash
   CONCURRENT_DOWNLOADS=20
   CONCURRENT_EMBEDDINGS=10
   ```

2. **Adjust Batch Size**: For better throughput
   ```bash
   BATCH_SIZE=50
   ```

3. **Optimize Image Size**: Smaller images = faster processing
   ```bash
   IMAGE_MAX_SIZE=96
   IMAGE_QUALITY=60
   ```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. NVIDIA API Rate Limits
```
Error: 429 Too Many Requests
```
**Solution**: Reduce `CONCURRENT_EMBEDDINGS` or add retry logic.

#### 2. Qdrant Connection Failed
```
Error: Cannot connect to Qdrant at http://localhost:6333
```
**Solution**: Ensure Qdrant is running:
```bash
docker ps | grep qdrant
```

#### 3. Image Download Failures
```
Error: Failed to download image from URL
```
**Solution**: Check network connectivity and URL validity. The pipeline automatically retries and continues with next images.

#### 4. Memory Issues
```
Error: Out of memory
```
**Solution**: Reduce `BATCH_SIZE` and `CONCURRENT_DOWNLOADS`:
```bash
BATCH_SIZE=10
CONCURRENT_DOWNLOADS=5
```

### Logs

Check detailed logs for debugging:
```bash
tail -f logs/pipeline.log
```

---

## 📚 API Reference

### ImageEmbeddingPipeline

Main processing pipeline class.

```python
from src.pipeline import ImageEmbeddingPipeline
from config.config import Config

config = Config.from_env()
pipeline = ImageEmbeddingPipeline(config)

# Process CSV file
success, failure = await pipeline.process_csv(
    csv_file="data/images.csv",
    start_from=0,      # Starting row index
    max_images=None    # None = process all
)
```

### ImageSearchEngine

Search engine for querying embeddings.

```python
from src.search_engine import ImageSearchEngine

engine = ImageSearchEngine(config)

# Search by text
results = await engine.search_by_text(
    query="black leather shoes",
    limit=10,
    score_threshold=0.5
)

# Search by image
results = await engine.search_by_image(
    image_path_or_url="path/to/image.jpg",
    limit=10,
    score_threshold=0.5
)

# Advanced search with filters
results = await engine.search_with_filters(
    query="women's watch",
    filename_pattern="*.jpg",
    limit=10
)

# Get collection statistics
stats = engine.get_collection_stats()
```

### SearchResult

Result object from search queries.

```python
@dataclass
class SearchResult:
    id: int              # Vector ID
    filename: str        # Product filename
    image_url: str       # Original image URL
    score: float         # Similarity score (0-1)
    processed_at: str    # ISO timestamp
```

---

## 🎓 How It Works

### Multimodal Embeddings

The pipeline uses **NVIDIA nv-embed-v1**, which generates unified embeddings for both images and text in the same vector space. This enables:

1. **Cross-Modal Search**: Query images with text, and vice versa
2. **Semantic Understanding**: Captures visual concepts, not just pixels
3. **Transfer Learning**: Pre-trained on massive datasets

### Vector Similarity

Similarity is computed using cosine distance in high-dimensional space:

```
similarity = cosine(query_vector, database_vector)
```

Higher scores (closer to 1.0) indicate greater visual/semantic similarity.

### Why 4096 Dimensions?

The 4096-dimensional vectors capture:
- Color distributions
- Textures and patterns
- Object shapes and structures
- Spatial relationships
- Semantic concepts

This high dimensionality enables nuanced similarity detection.

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Distributed processing with Ray or Dask
- [ ] Real-time inference API endpoint
- [ ] Advanced filtering (price, brand, category)
- [ ] Image quality assessment pre-processing
- [ ] MLOps integration (MLflow, Weights & Biases)
- [ ] Kubernetes deployment manifests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **NVIDIA NIM** for powerful multimodal embeddings
- **Qdrant** for efficient vector search
- **Myntra Fashion Dataset** for product images

---

## 📧 Support

For questions or issues:
- Open an issue on GitHub
- Check the [troubleshooting section](#-troubleshooting)
- Review logs in `logs/pipeline.log`

---

## 🚀 What's Next?

After processing your images, you can:

1. **Build a Visual Search UI**: Create a web interface for product discovery
2. **Integrate with Recommendation Systems**: Use embeddings for personalized suggestions
3. **Deploy as Microservice**: Expose search API for production use
4. **Add More Modalities**: Extend to video, audio, or 3D models

---

<div align="center">

**Built with ❤️ for Retail AI**

[Documentation](#) • [Examples](tests/) • [API Reference](#-api-reference)

</div>

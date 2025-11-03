# Customer Support Document Pipeline

A complete document processing pipeline for customer support PDFs using NVIDIA NeMo Retriever embeddings, Docling for extraction, and Qdrant for vector storage.

In detail blog with screenshot :- https://medium.com/@yash.kavaiya3/building-a-smart-customer-support-agent-using-nvidia-embedding-and-qdrant-vector-db-c5067aadb777

## Features

- **PDF Extraction**: Uses Docling library for robust PDF document parsing
- **Smart Chunking**: Hierarchical chunking that respects document structure
- **NVIDIA Embeddings**: State-of-the-art embeddings using `llama-3.2-nemoretriever-300m-embed-v2`
- **Vector Storage**: Efficient storage and retrieval using Qdrant
- **Reranking**: Improved relevance with `llama-3.2-nv-rerankqa-1b-v2`
- **SOLID Architecture**: Clean, maintainable code following best practices

## Architecture

```
PDFs → Docling Extraction → Hierarchical Chunking → NVIDIA Embeddings → Qdrant Storage
                                                                            ↓
User Query → Query Embedding ← Retrieval ← Reranking ← Vector Search
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Qdrant running locally or remotely
- NVIDIA API key from [build.nvidia.com](https://build.nvidia.com)

### Setup

1. **Clone and navigate to directory**:
```bash
cd customer_support
```

2. **Create virtual environment**:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
Copy `.env` and update with your NVIDIA API key (already configured in this repo).

### Start Qdrant

```bash
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant
```

## Usage

### Process Documents

Process all PDFs in the data directory:
```bash
python main.py process data
```

Process a single PDF:
```bash
python main.py process data/document.pdf
```

With custom log file:
```bash
python main.py process data --log-file logs/pipeline.log
```

### Search Documents

Search for relevant information:
```bash
python main.py search "What are the retail compliance requirements?"
```

With custom parameters:
```bash
python main.py search "safety regulations" --top-k 10 --threshold 0.7
```

### Get Collection Info

View database statistics:
```bash
python main.py info
```

## Configuration

Edit `.env` file to customize:

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY=nvapi-YOUR-KEY-HERE
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings
NVIDIA_RERANK_URL=https://integrate.api.nvidia.com/v1/ranking

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=customer_support_docs

# Processing Configuration
EMBEDDING_MODEL=nvidia/llama-3.2-nemoretriever-300m-embed-v2
RERANK_MODEL=nvidia/llama-3.2-nv-rerankqa-1b-v2
EMBEDDING_DIM=2048
CHUNK_SIZE=512
CHUNK_OVERLAP=50
BATCH_SIZE=10
REQUEST_TIMEOUT=60
```

Install below if you face some error
```
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx
```
## Module Overview

### `config/config.py`
- Configuration management using dataclasses
- Environment variable validation
- Type-safe configuration objects

### `src/data_ingestion.py`
- `PDFProcessor`: Extracts content from PDFs using Docling
- `DocumentExtractor`: High-level interface for document processing
- Handles errors gracefully with detailed metadata

### `src/chunking.py`
- `DocumentChunker`: Hierarchical chunking using Docling
- `ChunkProcessor`: Filters and validates chunks
- Maintains document structure and metadata

### `src/embedding.py`
- `EmbeddingGenerator`: Generates embeddings via NVIDIA API
- `DocumentEmbedder`: Batch processing for document chunks
- `Reranker`: Improves search relevance with reranking

### `src/qdrant_manager.py`
- `QdrantManager`: All vector database operations
- Collection management, insertion, and search
- Handles filtering and metadata storage

### `src/load_data.py`
- `CustomerSupportPipeline`: Main document processing pipeline
- `SearchPipeline`: Search and retrieval operations
- Coordinates all components following SOLID principles

## NVIDIA Models

### Embedding Model
**Model**: `nvidia/llama-3.2-nemoretriever-300m-embed-v2`
- **Dimensions**: 2048
- **Max tokens**: 8192
- **Parameters**: 300M
- **Input types**: 
  - `query` - For search queries
  - `passage` - For document chunks

### Reranker Model
**Model**: `nvidia/llama-3.2-nv-rerankqa-1b-v2`
- **Purpose**: Refine top-k results from vector search
- **Use case**: Improves relevance ranking after initial retrieval


## Data Files

The pipeline processes PDFs from the `data/` directory:
- `2015-31795.pdf`
- `RegulatedProductsHandbook.pdf`
- `Retail Program Standards Policy Statement July 2028.pdf`
- `tclc-fs-fedreg-retail-environ-2012.pdf`

## Logging

Logs are output to console by default. Specify `--log-file` to save to a file:
```bash
python main.py process data --log-file logs/pipeline.log
```

Log format includes:
- Timestamp
- Module name
- Log level
- Message

## Error Handling

The pipeline includes comprehensive error handling:
- Failed document processing continues with others
- Embedding failures are logged and skipped
- Database errors are caught and reported
- Full error details in logs

## Performance

- **Batch processing**: Configurable batch size for embeddings
- **Concurrent operations**: Async support for future optimization
- **Memory efficient**: Streams chunks to database
- **Rate limiting**: Built-in delays to respect API limits

## Troubleshooting

### "Import docling could not be resolved"
This is expected before installation. Run `pip install -r requirements.txt`.

### "NVIDIA_API_KEY must be set"
Ensure `.env` file has a valid NVIDIA API key starting with `nvapi-`.

### "Connection refused to Qdrant"
Start Qdrant using Docker: `docker run -d -p 6333:6333 qdrant/qdrant`

### "Embedding generation failed"
Check:
- NVIDIA API key is valid
- Internet connection is stable
- API rate limits not exceeded

## Development

### SOLID Principles

The codebase follows SOLID principles:
- **Single Responsibility**: Each class has one job
- **Open/Closed**: Easy to extend without modification
- **Liskov Substitution**: Components are interchangeable
- **Interface Segregation**: Focused interfaces
- **Dependency Injection**: Dependencies passed to constructors

### Testing

Add tests in a `tests/` directory:
```bash
pytest tests/ -v
```

# NVIDIA Retail AI Agent Teams

Multi-modal AI system combining document processing, image embeddings, and conversational AI for retail compliance and customer support.

<img width="758" height="512" alt="ChatGPT Image Nov 1, 2025, 06_09_53 PM" src="https://github.com/user-attachments/assets/79070147-b725-4052-934c-e965886e1130" />

<img width="800" height="900" alt="diagram-export-11-3-2025-5_19_08-PM" src="https://github.com/user-attachments/assets/44d6a405-321b-4b6e-a2fa-a8264a42f860" />


## 🎯 Key Features

## Customer Support Document Pipeline
A complete document processing pipeline for customer support PDFs using NVIDIA NeMo Retriever embeddings, Docling for extraction, and Qdrant for vector storage.

In detail blog with screenshot :- https://medium.com/@yash.kavaiya3/building-a-smart-customer-support-agent-using-nvidia-embedding-and-qdrant-vector-db-c5067aadb777

### Features
- PDF Extraction: Uses Docling library for robust PDF document parsing
- Smart Chunking: Hierarchical chunking that respects document structure
- NVIDIA Embeddings: State-of-the-art embeddings using llama-3.2-nemoretriever-300m-embed-v2
- Vector Storage: Efficient storage and retrieval using Qdrant
- Reranking: Improved relevance with llama-3.2-nv-rerankqa-1b-v2
- SOLID Architecture: Clean, maintainable code following best practices
### Image Embeddings
- Async image processing pipeline
- NVIDIA multimodal embeddings
- Fashion product search

### AI Agent
- CopilotKit integration
- Next.js 15 frontend
- Python agent backend

## 🔧 Technology Stack

- **Python 3.8+** - Backend processing
- **Next.js 15** - Frontend framework
- **NVIDIA AI** - Embeddings, reranking, OCR
- **Qdrant** - Vector database
- **Docling** - PDF extraction
- **CopilotKit** - AI agent framework
- **Docker** - Containerization

## 📚 Documentation

- [Document Pipeline Quick Start](Customer_support/Code/document_pipeline/QUICKSTART.md)
- [Document Pipeline README](Customer_support/Code/document_pipeline/README.md)
- [AI Agent Development Guide](.github/copilot-instructions.md)

## 🔑 NVIDIA Models Used

### Embeddings
- **Model**: `nvidia/llama-3.2-nemoretriever-300m-embed-v2`
- **Dimensions**: 2048
- **Token Limit**: 8192
- **Input Types**: `query` (search) / `passage` (documents)
- **Note**: "300m" refers to model parameters (300M), not embedding dimensions

### Reranker
- **Model**: `nvidia/llama-3.2-nv-rerankqa-1b-v2`
- **Purpose**: Refine top-k results for better precision
- **Usage**: After vector search

## 🚀 Usage Examples

### Process Documents
```bash
cd Customer_support/Code/document_pipeline
python main.py process ../Data
```

### Search Documents
```bash
python main.py search "environmental compliance standards"
```

### Interactive Search
```bash
python main.py interactive
```

### Process Images
```bash
cd image_embeddings_pipeline
python main.py 0 100 data/images.csv
```

## 🏗️ Architecture Principles

This project follows **SOLID principles**:

- ✅ **Single Responsibility** - Each class has one job
- ✅ **Open/Closed** - Easy to extend without modification
- ✅ **Liskov Substitution** - Implementations follow interfaces
- ✅ **Interface Segregation** - Clean, focused interfaces
- ✅ **Dependency Injection** - Components receive dependencies

See [Customer_support/Code/document_pipeline/](Customer_support/Code/document_pipeline/) for excellent examples of clean architecture.

## 🔍 How It Works

### Document Processing Flow
```
PDF → Docling Extraction → Text Chunks → NVIDIA Embeddings → Qdrant
                                                                 ↓
Query → NVIDIA Embeddings → Vector Search → Reranker → Results
```

### Image Processing Flow
```
CSV → Download Images → Resize/Encode → NVIDIA Embeddings → Qdrant
                                                              ↓
Query/Image → NVIDIA Embeddings → Vector Search → Results
```

## 📝 Configuration

API keys and settings are in `.env` files:
- `Customer_support/Code/document_pipeline/.env` - Document processing config
- `image_embeddings_pipeline/.env` - Image processing config

## 🐛 Troubleshooting

### Collection not found
Run processing first to index documents/images

### No results found
- Check Qdrant: http://localhost:6333/dashboard
- Try broader search queries
- Lower score threshold in config

### Import errors
```bash
pip install -r requirements.txt
```

### Qdrant not running
```bash
docker ps  # Check if running
docker start qdrant  # Or start new container
```

## 📄 License

MIT

## 🙏 Acknowledgments

- NVIDIA AI for state-of-the-art models
- Docling for PDF extraction
- Qdrant for vector search
- CopilotKit for AI agent framework

# RAG System

A Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, PostgreSQL, pgvector and OpenAI

## Features

- **Document Upload**: Upload PDF, DOCX, TXT, MD files
- **Text Extraction**: Automatic text extraction from documents
- **Smart Chunking**: Text splitting with RecursiveCharacterTextSplitter (Langchain)
- **Embeddings**: Generate embeddings using OpenAI
- **Semantic Search**: Similarity search powered by pgvector
- **RAG Query**: Document-based question answering with GPT-4
- **REST API**: Interface to interact with the system

## Workflow

User Query -> FastAPI (Routing) -> Similarity Search (pgvector) -> Context Building -> OpenAI GPT-4 -> Response + Sources

## Quick Start

### Prerequisites

- Docker
- Python
- OpenAI API Key

### Installation

```
1. Clone repository:

git clone https://github.com/peps984/rag-system.git
cd rag-system

2. Setup environment:

cp .env.example .env # Edit .env and add your OPENAI_API_KEY

3. Start with Docker:

docker compose up -d

4. Verify:

curl http://localhost:8000/health
```

### Access

- **API**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Usage

```
1. Upload Document:

curl -X POST "http://localhost:8000/documents/upload" -F "file=@document.pdf"

2. Ask a Question:

curl -X POST "http://localhost:8000/query?question=How+does+the+product+work"

3. Semantic Search:

curl -X POST "http://localhost:8000/search?query=installation&top_k=5"
```

## Testing

```
Install dev dependencies:

pip install -r requirements.txt

Run end-to-end test:

python scripts/test_rag_flow.py
```

## Project Structure

```
rag-system/
├── api/
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Pydantic schemas
├── config/
│   └── settings.py        # Configuration
├── database/
│   ├── database.py        # DB connection
│   └── models.py          # SQLAlchemy models
├── processing/
│   ├── text_extractor.py  # Text extraction script
│   ├── extractors.py      # Text extractors splitted by file extension
│   ├── embedding_generator.py  # Embeddings
│   ├── similarity_search.py    # Search
│   └── rag_service.py     # Complete RAG
├── scripts/
│   └── test_rag_flow.py   # E2E tests
├── compose.yaml
├── Dockerfile
└── main.py                # Entry point
```

## 📊 API Endpoints

### Documents

- `POST /documents/upload` - Upload document
- `GET /documents` - List documents
- `GET /documents/{id}` - Get document details
- `GET /documents/{id}/chunks` - Get document chunks
- `DELETE /documents/{id}` - Delete document
- `POST /documents/{id}/generate-embeddings` - Generate embeddings (optional)

### Search & Query

- `POST /search` - Semantic search
- `POST /query` - RAG query with generated answer

See complete documentation at `/docs`

## Development

## Database Schema

### documents
- `id` - Primary key
- `filename` - File name on disk
- `original_filename` - Original file name
- `file_path` - Complete path
- `file_size` - Size in bytes
- `file_type` - Extension (pdf, docx, txt, md)
- `content` - Extracted text
- `content_length` - Text length

### document_chunks
- `id` - Primary key
- `document_id` - FK → documents
- `chunk_index` - Position in document
- `content` - Chunk text
- `char_count` - Character count
- `created_at` - Timestamp
- `embedding` - Vector(1536) for similarity search

## How RAG Works

1. **Upload**: Document uploaded (max file size: 10 MB) -> text extracted
2. **Chunking**: Text split into ~1000 character pieces with overlap of ~200
3. **Embedding**: Each chunk -> 1536D vector (OpenAI)
4. **Storage**: Embeddings stored in PostgreSQL with pgvector
5. **Query**: 
   - User query -> embedding
   - Search top-K similar chunks (cosine similarity)
   - Chunks -> context for GPT-4
   - GPT-4 generates answer based on context
6. **Response**: Answer + cited sources

## Contributing

Contributions are welcome! 

## Roadmap

Current:
- [x] Document upload and processing
- [x] Text chunking
- [x] Embeddings generation
- [x] Semantic search with cosine similarity
- [x] RAG query endpoint

Future:
- [ ] Streaming responses
- [ ] Conversation history
- [ ] Document versioning
- [ ] Fine-tuned embeddings
- [ ] Dashboard UI
- [ ] ...

## License

MIT License - see [LICENSE](LICENSE) file for details

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [pgvector](https://github.com/pgvector/pgvector)
- [OpenAI](https://openai.com/)
- [Langchain](https://www.langchain.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

## Contact

For questions or support, open an issue on GitHub.

---

**If you find this project useful, give it a star!**
# Domain-Expert RAG Assistant (Enterprise Edition)

A production-grade Retrieval Augmented Generation (RAG) system designed for high-stakes domains (Finance, Legal, Medical). 

## 🚀 Features
- **Async Ingestion Pipeline:** Decoupled PDF processing using Celery & Redis to handle large files without blocking the API.
- **Hybrid Search:** Combines Keyword (BM25) and Vector (Cosine) search for maximum recall.
- **Reranking:** Uses Cross-Encoders (Cohere) to refine retrieval results.
- **Deduplication:** SHA-256 hashing prevents processing the same document twice.
- **Rate Limiting:** Protects LLM endpoints from abuse.
- **Observability:** Full tracing via LangSmith.

## 🛠 Tech Stack
- **Backend:** FastAPI, Python 3.12
- **Frontend:** Next.js 14, Tailwind CSS
- **Vector DB:** Pinecone (Serverless)
- **Database:** PostgreSQL (Metadata & User Data)
- **Queue:** Redis (Task Broker)
- **Storage:** MinIO (S3-compatible object storage)
- **Orchestration:** LlamaIndex / LangChain

## 📂 Project Structure
```text
/backend
  ├── /app
  │   ├── /api            # REST Endpoints
  │   ├── /services       # Business Logic (Ingest, Search)
  │   └── /models         # Database Schemas
  ├── /worker             # Celery Background Workers
  └── pyproject.toml      # Dependency Management
/frontend                 # Next.js UI
/infrastructure           # Docker Compose (DB, Redis, MinIO)
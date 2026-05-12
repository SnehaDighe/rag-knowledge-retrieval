# RAG Knowledge Retrieval System

## 1. What this project does

This project is a **Retrieval-Augmented Generation (RAG)** knowledge retrieval system. It answers questions by:

- ingesting documents from local text files
- converting text into semantic vector embeddings
- storing embeddings in a vector search index (FAISS)
- matching queries to the most relevant document chunks
- returning results with similarity scores and source context

It is designed to provide grounded answers from actual documents instead of relying only on an LLM's internal knowledge.

## 2. What is the need for this project

The project exists because standard LLMs often **hallucinate** or produce inaccurate responses when asked about specific internal data. It is useful for:

- domain-specific knowledge retrieval
- technical documentation search
- customer support knowledge bases
- reducing LLM hallucinations
- providing evidence-based results

By grounding search results in real documents, it increases reliability and trust.

## 3. Why it is built this way

### Key design decisions

- **Retrieval-first architecture**: Query embedding → semantic search → relevant document chunks
- **FAISS vector search**: Fast similarity search for embeddings
- **Chunking with overlap**: Preserves context across long documents
- **OpenAI embeddings**: Converts text meaning into numeric vectors
- **Environment configuration**: Uses `.env` for API keys and settings

### Why not a plain LLM?

A plain LLM is less reliable because it may:
- invent facts not present in the source data
- lose the ability to cite sources
- fail on domain-specific details not learned during training

This project avoids those risks by basing answers on source documents.

## 4. How it is built

### `requirements.txt`

The project depends on:

- `openai`: OpenAI API client
- `faiss-cpu`: Local vector search engine
- `flask`: Python web framework
- `python-dotenv`: Loads environment variables
- `numpy`: Numerical operations and vectors
- `requests`, `beautifulsoup4`, `pydantic`, `pandas`: supporting utilities

### `src/main.py`

This is the entry point.

- loads environment variables
- configures logging
- initializes `DataIngestion`, `EmbeddingsGenerator`, and `SemanticSearch`
- ingests documents and creates chunks
- generates embeddings for chunks
- builds the search index
- performs an example query

### `src/data_ingestion.py`

Responsible for:

- reading `.txt` files from `DATA_PATH`
- storing document metadata
- splitting content into overlapping chunks for embedding

### `src/embeddings.py`

Responsible for:

- creating an OpenAI client
- generating embeddings for text
- processing texts in sequence
- logging errors and progress

### `src/semantic_search.py`

Responsible for:

- building a FAISS index from embeddings
- performing vector search with query embeddings
- falling back to NumPy cosine similarity if FAISS is unavailable

## 5. Edge cases, side effects, and effects of components

### Positive effects

- reduces hallucination by grounding answers in documents
- enables semantic matching beyond keywords
- supports fast retrieval with FAISS
- supports configurable chunking and deployment

### Edge cases and limitations

- expects only `.txt` files in `data/documents`
- loads all documents into memory
- may fail or perform poorly for very large datasets
- relies on OpenAI API keys and usage quota
- chunk boundaries can split meaning across text
- no persistence for embeddings or search index currently

### Side effects

- API costs when generating embeddings
- potential quota or rate-limit errors from OpenAI
- local RAM usage for FAISS index and embeddings
- dependency on OpenAI and environment configuration

## 6. Running the project

1. create or copy `.env` from `.env.example`
2. set `OPENAI_API_KEY`
3. activate the environment
4. run:

```bash
.venv/bin/python src/main.py
```

If you want to make this more production-ready, the next steps are:

- add embedding persistence
- batch embedding generation
- add error handling for missing or invalid files
- support additional file formats
- add a web API endpoint and frontend


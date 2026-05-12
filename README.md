# RAG-based Knowledge Retrieval System

A comprehensive knowledge retrieval system that answers domain-specific questions using LLM APIs and vector databases. This system combines data ingestion, semantic search, and intelligent response generation.

## Features

- **Data Ingestion Pipeline**: Handle structured and unstructured data
- **Embedding Generation**: Create vector embeddings for documents
- **Semantic Search**: Fast and relevant document retrieval using FAISS/Pinecone
- **Multi-Backend Support**: Python Flask and Node.js Express services
- **LLM Integration**: OpenAI API for intelligent responses
- **Containerization**: Docker and Kubernetes support

## Tech Stack

- **Backend**: Python (Flask), Node.js (Express.js)
- **LLM & APIs**: OpenAI API
- **Vector DB**: FAISS, Pinecone
- **Data Processing**: Python
- **Containerization**: Docker, Kubernetes

## Project Structure

```
rag-knowledge-retrieval/
├── src/
│   ├── main.py
│   ├── data_ingestion.py
│   ├── embeddings.py
│   ├── semantic_search.py
│   └── utils.py
├── backend-python/
│   ├── app.py (Flask)
│   └── routes/
├── backend-nodejs/
│   ├── package.json
│   └── server.js
├── config/
│   └── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker (optional)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rag-knowledge-retrieval.git
cd rag-knowledge-retrieval
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Python Backend (Flask)

```bash
cd backend-python
python app.py
```

### Node.js Backend (Express)

```bash
cd backend-nodejs
npm install
npm start
```

## Docker

Build and run with Docker:

```bash
docker-compose up --build
```

## API Endpoints

### Authentication Endpoints

- `POST /auth/signup` - Create a new user account
- `POST /auth/login` - Login and get JWT token
- `GET /auth/verify` - Verify JWT token validity

### Protected Endpoints (Require JWT Token)

- `POST /api/ingest` - Ingest documents (requires `Authorization: Bearer <token>`)
- `POST /api/query` - Query the knowledge base (requires `Authorization: Bearer <token>`)
- `GET /api/status` - System status (requires `Authorization: Bearer <token>`)

### Public Endpoints

- `GET /health` - Health check (no authentication required)

## Authentication

This system uses JWT (JSON Web Tokens) for authentication. All API endpoints except `/health` require authentication.

### Authentication Flow

1. **Signup**: Create a user account
```bash
curl -X POST http://localhost:3000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

2. **Login**: Get JWT token
```bash
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

3. **Use API**: Include token in Authorization header
```bash
curl -X GET http://localhost:3000/api/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Testing Authentication

Run the authentication test script:
```bash
./test_auth.sh
```

## Contributing

Contributions welcome! Please create a pull request with your changes.

## Case Study

Detailed project context and the product vision are available in `CASE_STUDY.md`.

## License

MIT License

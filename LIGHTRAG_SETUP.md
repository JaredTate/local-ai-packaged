# LightRAG Setup Guide

## Overview
LightRAG has been integrated into the docker-compose stack using Memgraph as the graph storage backend.

## Configuration Requirements

### 1. Environment Variables (.env file)
Before starting LightRAG, you MUST configure the following in your `.env` file:

```bash
# LightRAG LLM Configuration (REQUIRED)
LIGHTRAG_LLM_BINDING=openai
LIGHTRAG_LLM_MODEL=gpt-4o
LIGHTRAG_LLM_BINDING_HOST=https://api.openai.com/v1
LIGHTRAG_LLM_API_KEY=your_actual_openai_api_key_here  # MUST REPLACE

# LightRAG Embedding Configuration (REQUIRED)
LIGHTRAG_EMBEDDING_BINDING=openai
LIGHTRAG_EMBEDDING_MODEL=text-embedding-3-large
LIGHTRAG_EMBEDDING_DIM=3072
LIGHTRAG_EMBEDDING_BINDING_HOST=https://api.openai.com
LIGHTRAG_EMBEDDING_API_KEY=your_actual_openai_api_key_here  # MUST REPLACE

# Optional: Set a hostname for external access
LIGHTRAG_HOSTNAME=lightrag.yourdomain.com  # Optional for Caddy reverse proxy
```

### Alternative LLM/Embedding Options:

#### Option A: Using Ollama (if you have Ollama service running)
```bash
# LLM Configuration for Ollama
LIGHTRAG_LLM_BINDING=ollama
LIGHTRAG_LLM_MODEL=qwen2.5:7b-instruct-q4_K_M  # or any model you have
LIGHTRAG_LLM_BINDING_HOST=http://host.docker.internal:11434
LIGHTRAG_LLM_API_KEY=not_needed_for_ollama

# Embedding Configuration for Ollama
LIGHTRAG_EMBEDDING_BINDING=ollama
LIGHTRAG_EMBEDDING_MODEL=bge-m3:latest  # or nomic-embed-text
LIGHTRAG_EMBEDDING_DIM=1024
LIGHTRAG_EMBEDDING_BINDING_HOST=http://host.docker.internal:11434
LIGHTRAG_EMBEDDING_API_KEY=not_needed_for_ollama
```

#### Option B: Using other OpenAI-compatible services (e.g., OpenRouter, Azure)
```bash
# Example for OpenRouter
LIGHTRAG_LLM_BINDING=openai
LIGHTRAG_LLM_MODEL=google/gemini-2.5-flash
LIGHTRAG_LLM_BINDING_HOST=https://openrouter.ai/api/v1
LIGHTRAG_LLM_API_KEY=your_openrouter_api_key
```

## Directory Structure
The following directories will be created automatically:
```
lightrag/
├── config.ini           # Memgraph connection config
└── data/
    ├── rag_storage/     # LightRAG knowledge graph storage
    ├── inputs/          # Documents to process
    └── tiktoken/        # Token cache for offline use
```

## Service Details

### Ports
- **9621**: LightRAG Web UI and API (exposed)
- Access via browser: `http://your-server:9621` or through Caddy at port 8009

### Storage Configuration
- **Graph Storage**: Memgraph (already in your stack)
- **KV Storage**: JsonKVStorage (local file storage)
- **Document Status**: JsonDocStatusStorage
- **Vector Storage**: NanoVectorDBStorage (embedded)

### Memgraph Connection
LightRAG connects to your existing Memgraph instance using:
- Host: `memgraph` (internal Docker network)
- Port: `7687` (Bolt protocol)
- Username: `memgraph` (from MEMGRAPH_USER env)
- Password: `memgraph` (from MEMGRAPH_PASSWORD env)

## Starting the Service

1. **Ensure all environment variables are set** in `.env`

2. **Start the services**:
```bash
docker compose up -d lightrag
```

3. **Check logs**:
```bash
docker compose logs -f lightrag
```

4. **Access the Web UI**:
- Direct: `http://your-server:9621`
- Via Caddy: `http://your-server:8009` (or your configured LIGHTRAG_HOSTNAME)

## Usage

### Web UI Features
- Document upload and indexing
- Knowledge graph visualization
- Query interface with multiple modes:
  - Naive: Simple vector search
  - Local: Entity-focused search
  - Global: High-level concept search
  - Hybrid: Combined approach

### API Endpoints
- `POST /api/insert_text` - Insert text documents
- `POST /api/insert_file` - Upload files
- `POST /api/query` - Query the knowledge graph
- `GET /api/status` - Check service status

### Ollama-Compatible API
LightRAG also provides an Ollama-compatible API at:
- `POST /v1/chat/completions` - Chat completions endpoint

## Important Notes

1. **API Keys**: You MUST provide valid API keys for your chosen LLM and embedding services
2. **Embedding Model Consistency**: Once you index documents with an embedding model, you MUST use the same model for queries
3. **Memgraph Data**: The graph data is stored in Memgraph, which persists in `./memgraph/data/`
4. **Document Storage**: Processed documents and metadata are stored in `./lightrag/data/rag_storage/`

## Troubleshooting

### Common Issues:

1. **Connection to Memgraph fails**:
   - Ensure Memgraph is running: `docker compose ps memgraph`
   - Check Memgraph logs: `docker compose logs memgraph`

2. **LLM/Embedding API errors**:
   - Verify API keys are correct
   - Check API endpoint URLs
   - Ensure you have credits/quota for the APIs

3. **Out of memory errors**:
   - Increase Docker memory limits
   - Reduce `MAX_ASYNC` and `MAX_PARALLEL_INSERT` values

4. **Port conflicts**:
   - Change the port mapping in docker-compose.yml if 9621 is already in use

## Updating Configuration

If you need to change LLM or embedding models:
1. Stop the service: `docker compose stop lightrag`
2. Update `.env` file
3. If changing embedding model, clear the storage: `rm -rf ./lightrag/data/rag_storage/*`
4. Restart: `docker compose up -d lightrag`

## Security Considerations

- Keep API keys secure and never commit them to version control
- Consider using Docker secrets for production deployments
- The service is exposed on port 9621 - use firewall rules or reverse proxy for access control
- Memgraph credentials should be changed from defaults in production
# Updated .env for Server (Memgraph without authentication)

Since the newer Memgraph version doesn't support the old authentication flags, update your `.env` file:

```env
# LightRAG Graph Storage Configuration
LIGHTRAG_GRAPH_STORAGE=MemgraphStorage

# Memgraph connection for LightRAG (no auth required now)
MEMGRAPH_URI=bolt://host.docker.internal:7688
MEMGRAPH_USERNAME=
MEMGRAPH_PASSWORD=
MEMGRAPH_DATABASE=memgraph

# Alternative: If host.docker.internal doesn't work, try:
# MEMGRAPH_URI=bolt://172.17.0.1:7688  # Docker bridge IP
# or
# MEMGRAPH_URI=bolt://memgraph:7687  # If containers can see each other

# LightRAG LLM Configuration
LIGHTRAG_LLM_BINDING=openai
LIGHTRAG_LLM_MODEL=gpt-4o-mini
LIGHTRAG_LLM_BINDING_HOST=https://api.openai.com/v1
LIGHTRAG_LLM_API_KEY=YOUR_NEW_API_KEY_HERE

# LightRAG Embedding Configuration
LIGHTRAG_EMBEDDING_BINDING=openai
LIGHTRAG_EMBEDDING_MODEL=text-embedding-3-small
LIGHTRAG_EMBEDDING_DIM=1536
LIGHTRAG_EMBEDDING_BINDING_HOST=https://api.openai.com/v1
LIGHTRAG_EMBEDDING_API_KEY=YOUR_NEW_API_KEY_HERE
```

## Steps on your server:

1. **Pull the updated docker-compose.yml** from this repo
2. **Update your .env** with the configuration above (empty username/password)
3. **Restart Memgraph**:
   ```bash
   docker compose -p localai stop memgraph
   docker compose -p localai rm -f memgraph
   docker compose -p localai up -d memgraph
   ```
4. **Wait for Memgraph to start** (check logs):
   ```bash
   docker logs localai-memgraph-1 --tail 20
   ```
5. **Restart LightRAG**:
   ```bash
   docker compose -p localai restart lightrag
   ```
6. **Check LightRAG logs**:
   ```bash
   docker logs lightrag --tail 50
   ```

## If containers still can't connect:

Try using the Docker bridge IP directly:
```bash
# Find Docker bridge IP
ip addr show docker0 | grep inet | awk '{print $2}' | cut -d/ -f1

# Usually it's 172.17.0.1, so in .env:
MEMGRAPH_URI=bolt://172.17.0.1:7688
```
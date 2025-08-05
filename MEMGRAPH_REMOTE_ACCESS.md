# Memgraph Remote Access Setup Guide

This guide explains how to set up remote access to your Memgraph database through Cloudflare.

## Current Setup

- **Memgraph Lab (Web UI)**: https://mem.jaredtate.com/ (port 3003)
- **Memgraph Database**: Running on port 7687 (Bolt protocol) internally, exposed as 7688 externally
- **Docker Network**: Internal connection string: `bolt://memgraph@memgraph:7687/memgraph`

## The Challenge

Cloudflare Tunnels natively support HTTP/HTTPS traffic but not the Bolt protocol (binary protocol used by Memgraph/Neo4j). You have several options:

## Solution Options

### Option 1: Cloudflare TCP Tunnel (Recommended)

1. **Update your Cloudflare tunnel configuration** (`cloudflare-tunnel-config.yml`):
   ```yaml
   tunnel: YOUR_TUNNEL_ID
   credentials-file: /path/to/credentials.json

   ingress:
     # Existing HTTP services
     - hostname: mem.jaredtate.com
       service: http://localhost:3003
     
     # TCP tunnel for Memgraph Bolt protocol
     - hostname: memgraph-bolt.jaredtate.com
       service: tcp://localhost:7688
       originRequest:
         proxyType: tcp
     
     # Catch-all rule
     - service: http_status:404
   ```

2. **Run the tunnel**:
   ```bash
   cloudflared tunnel --config cloudflare-tunnel-config.yml run
   ```

3. **Connect from Python**:
   ```python
   URI = "bolt://memgraph-bolt.jaredtate.com:7687"
   AUTH = ("memgraph", "your_password")
   ```

### Option 2: SSH Tunnel

1. **Create an SSH tunnel** from your local machine:
   ```bash
   ssh -L 7687:localhost:7688 your-server-user@your-server-ip
   ```

2. **Connect locally**:
   ```python
   URI = "bolt://localhost:7687"
   AUTH = ("memgraph", "your_password")
   ```

### Option 3: VPN Access

Set up a VPN to your server network and connect directly to the internal IP.

## Python Connection Examples

### Install Dependencies
```bash
pip install -r requirements-memgraph.txt
```

### Basic Connection
```python
from neo4j import GraphDatabase

URI = "bolt://localhost:7688"  # or your remote endpoint
AUTH = ("memgraph", "memgraph")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connected successfully!")
```

### Using GQLAlchemy (Memgraph's Python OGM)
```python
from gqlalchemy import Memgraph

memgraph = Memgraph(
    host='localhost',
    port=7688,
    username='memgraph',
    password='memgraph'
)

results = memgraph.execute_and_fetch("MATCH (n) RETURN count(n) as count")
```

## Security Considerations

1. **Always use strong passwords** - Update the default `memgraph/memgraph` credentials
2. **Use SSL/TLS when possible** - Consider setting up SSL certificates for Bolt connections
3. **Limit access** - Use firewall rules or Cloudflare Access to restrict who can connect
4. **Monitor connections** - Keep logs of connection attempts

## Environment Variables

Create a `.env` file for your credentials:
```env
MEMGRAPH_USER=memgraph
MEMGRAPH_PASSWORD=your_secure_password
```

## Testing Your Connection

Run the provided example script:
```bash
python memgraph_remote_connection.py
```

This will test various connection methods and verify connectivity.

## Troubleshooting

1. **Connection refused**: Check if Memgraph is running and ports are properly exposed
2. **Authentication failed**: Verify credentials in docker-compose.yml
3. **Timeout**: Check firewall rules and Cloudflare tunnel status
4. **SSL errors**: If using self-signed certificates, you may need to configure SSL verification

## Next Steps

1. Set up proper authentication with strong passwords
2. Configure SSL/TLS for encrypted connections
3. Set up monitoring and alerting for your Memgraph instance
4. Consider using Cloudflare Access for additional security
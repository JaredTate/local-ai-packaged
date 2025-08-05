#!/usr/bin/env python3
"""
Memgraph Remote Client - Connect over the internet via HTTP API
"""

import requests
import json

class MemgraphRemoteClient:
    def __init__(self, api_url="https://memgraph-api.jaredtate.com"):
        self.api_url = api_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if the API is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/health")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query(self, cypher_query, parameters=None):
        """Execute a read query"""
        try:
            response = self.session.post(
                f"{self.api_url}/query",
                json={
                    "query": cypher_query,
                    "parameters": parameters or {}
                }
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute(self, cypher_query, parameters=None):
        """Execute a write query"""
        try:
            response = self.session.post(
                f"{self.api_url}/execute",
                json={
                    "query": cypher_query,
                    "parameters": parameters or {}
                }
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    # Connect to your Memgraph instance over the internet
    client = MemgraphRemoteClient("https://memgraph-api.jaredtate.com")
    
    print("🔌 Connecting to Memgraph over the internet...")
    
    # Check health
    health = client.health_check()
    print(f"Health check: {health}")
    
    # Example queries
    print("\n📊 Running queries...")
    
    # Count nodes
    result = client.query("MATCH (n) RETURN count(n) as count")
    if result.get("success"):
        print(f"Number of nodes: {result['data'][0]['count']}")
    
    # Create a node
    result = client.execute(
        "CREATE (n:Person {name: $name, age: $age}) RETURN n",
        {"name": "Alice", "age": 30}
    )
    if result.get("success"):
        print(f"Created node - Nodes created: {result['nodes_created']}")
    
    # Query the created node
    result = client.query("MATCH (n:Person {name: 'Alice'}) RETURN n")
    if result.get("success") and result['data']:
        print(f"Found person: {result['data'][0]}")
    
    print("\n✅ You can now connect to Memgraph from anywhere!")
#!/usr/bin/env python3
"""
HTTP API Proxy for Memgraph
Provides a REST API that can be accessed through Cloudflare HTTP tunnels
"""

from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Memgraph connection
MEMGRAPH_URI = "bolt://memgraph:7687"  # Internal Docker connection
MEMGRAPH_AUTH = (
    os.getenv("MEMGRAPH_USER", "memgraph"),
    os.getenv("MEMGRAPH_PASSWORD", "memgraph")
)

driver = GraphDatabase.driver(MEMGRAPH_URI, auth=MEMGRAPH_AUTH)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        driver.verify_connectivity()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/query', methods=['POST'])
def execute_query():
    """Execute a Cypher query"""
    try:
        data = request.json
        query = data.get('query')
        parameters = data.get('parameters', {})
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        with driver.session() as session:
            result = session.run(query, parameters)
            records = [record.data() for record in result]
            
        return jsonify({
            "success": True,
            "data": records,
            "count": len(records)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/execute', methods=['POST'])
def execute_write():
    """Execute a write transaction"""
    try:
        data = request.json
        query = data.get('query')
        parameters = data.get('parameters', {})
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        with driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query, parameters)
                summary = result.consume()
                tx.commit()
        
        return jsonify({
            "success": True,
            "nodes_created": summary.counters.nodes_created,
            "relationships_created": summary.counters.relationships_created,
            "properties_set": summary.counters.properties_set
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
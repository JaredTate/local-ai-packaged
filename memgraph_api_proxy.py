from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
import os

app = Flask(__name__)
CORS(app)

# Connect to Memgraph inside Docker network
MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://memgraph:7687")
MEMGRAPH_USER = os.getenv("MEMGRAPH_USER", "memgraph")
MEMGRAPH_PASSWORD = os.getenv("MEMGRAPH_PASSWORD", "memgraph")

driver = GraphDatabase.driver(MEMGRAPH_URI, auth=(MEMGRAPH_USER, MEMGRAPH_PASSWORD))

@app.route('/health', methods=['GET'])
def health():
    try:
        driver.verify_connectivity()
        return jsonify({"status": "healthy", "message": "Connected to Memgraph"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/query', methods=['POST'])
def execute_query():
    try:
        data = request.json
        query = data.get('query')
        params = data.get('params', {})
        
        with driver.session() as session:
            result = session.run(query, params)
            records = []
            for record in result:
                records.append(dict(record))
            
            return jsonify({
                "success": True,
                "data": records,
                "summary": {
                    "counters": dict(result.consume().counters)
                }
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/transaction', methods=['POST'])
def execute_transaction():
    try:
        data = request.json
        queries = data.get('queries', [])
        
        with driver.session() as session:
            def work(tx):
                results = []
                for q in queries:
                    result = tx.run(q['query'], q.get('params', {}))
                    records = [dict(record) for record in result]
                    results.append(records)
                return results
            
            results = session.execute_write(work)
            
            return jsonify({
                "success": True,
                "data": results
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
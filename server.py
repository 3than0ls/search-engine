from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
from pathlib import Path
import os
sys.path.append('..')
from engine.inverted_index import InvertedIndex
from utils.config import load_config

app = Flask(__name__)
CORS(app)

load_config()
index_dir = Path(os.environ.get('INDEX_DIR', './index'))

try:
    inverted_index = InvertedIndex(index_dir)
    print(f"Inverted index loaded successfully from {index_dir}")
except FileNotFoundError:
    print(f"Error: Inverted index file not found at {index_dir}. Please run the indexer first.")
    inverted_index = None

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query', default='', type=str)
    try:
        results = inverted_index.ranked_retrieve(query)
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
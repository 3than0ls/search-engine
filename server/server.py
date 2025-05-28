from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query', default='', type=str)




    return jsonify({'result': query})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
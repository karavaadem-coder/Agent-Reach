from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Agent Reach API Çalışıyor",
        "endpoints": {
            "/twitter/search": "Twitter arama (kullanım: ?q=bitcoin&limit=5)"
        }
    })

@app.route('/twitter/search', methods=['GET'])
def twitter_search():
    query = request.args.get('q', 'bitcoin')
    limit = request.args.get('limit', 5)
    
    try:
        cmd = ['twitter', 'search', query, '--limit', str(limit)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return jsonify({
            "success": True,
            "query": query,
            "limit": limit,
            "output": result.stdout
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

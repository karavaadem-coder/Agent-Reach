# app.py - Bu dosyayı oluştur ve GitHub'a yükle
import subprocess
import json
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Agent Reach API Çalışıyor",
        "endpoints": {
            "/twitter/search?q=bitcoin&limit=5": "Twitter arama",
            "/agent-reach/doctor": "Sistem durumu"
        }
    })

@app.route('/twitter/search')
def twitter_search():
    query = request.args.get('q', 'bitcoin')
    limit = request.args.get('limit', 5)
    
    try:
        # Agent Reach'in twitter komutunu çalıştır
        cmd = ['twitter', 'search', query, '--limit', str(limit)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            "success": True,
            "command": " ".join(cmd),
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Zaman aşımı"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent-reach/doctor')
def doctor():
    try:
        result = subprocess.run(
            ['agent-reach', 'doctor'],
            capture_output=True,
            text=True
        )
        return jsonify({
            "status": "ok",
            "output": result.stdout
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

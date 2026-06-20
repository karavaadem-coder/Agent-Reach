from flask import Flask, request, jsonify
import subprocess
import os
import requests
import json
import re

app = Flask(__name__)

# Telegram ve Twitter bilgileri (Render env'den alınacak)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
TWITTER_AUTH_TOKEN = os.environ.get('TWITTER_AUTH_TOKEN', '')
TWITTER_CT0 = os.environ.get('TWITTER_CT0', '')

@app.route('/')
def home():
    return jsonify({
        "status": "Telegram Twitter Bot Çalışıyor!",
        "endpoints": {
            "/webhook": "Telegram webhook (POST)",
            "/search": "Twitter arama test (GET)"
        }
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram'dan gelen mesajları işler"""
    try:
        data = request.get_json()
        print(f"📩 Gelen mesaj: {data}")

        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')

            if text == '/start':
                send_message(chat_id, "🤖 **Twitter Bot'una Hoş Geldin!**\n\nKullanım:\n`/search kelime sayı`\nÖrnek: `/search bitcoin 5`")
                return jsonify({"status": "ok"})

            if text.startswith('/search'):
                parts = text.split(' ')
                if len(parts) >= 2:
                    query = parts[1]
                    limit = parts[2] if len(parts) >= 3 else 5
                    send_message(chat_id, f"🔍 `{query}` aranıyor... ⏳")
                    result = twitter_search(query, limit)
                    send_message(chat_id, result)
                else:
                    send_message(chat_id, "❌ Kullanım: `/search kelime sayı`")
            else:
                send_message(chat_id, "❌ Bilinmeyen komut. `/search kelime sayı` yaz.")

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"❌ Hata: {e}")
        return jsonify({"error": str(e)}), 500

def twitter_search(query, limit):
    """Twitter araması yapar"""
    try:
        os.environ['TWITTER_AUTH_TOKEN'] = TWITTER_AUTH_TOKEN
        os.environ['TWITTER_CT0'] = TWITTER_CT0

        cmd = ['twitter', 'search', query, '-n', str(limit)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.stdout:
            tweets = [t for t in result.stdout.strip().split('\n') if t.strip()]
            if not tweets:
                return f"❌ '{query}' için sonuç bulunamadı."
            formatted = f"🔍 **'{query}' için {len(tweets[:limit])} tweet:**\n\n"
            for i, tweet in enumerate(tweets[:limit], 1):
                tweet_text = tweet[:200] + "..." if len(tweet) > 200 else tweet
                formatted += f"{i}. {tweet_text}\n"
            return formatted
        else:
            return f"❌ '{query}' için sonuç bulunamadı."
    except Exception as e:
        return f"❌ Hata: {str(e)}"

def send_message(chat_id, text):
    """Telegram'a mesaj gönderir"""
    try:
        url = f"{TELEGRAM_URL}/sendMessage"
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
        response = requests.post(url, json=payload)
        print(f"📤 Mesaj gönderildi: {response.status_code}")
    except Exception as e:
        print(f"❌ Mesaj gönderme hatası: {e}")

@app.route('/search', methods=['GET'])
def test_search():
    query = request.args.get('q', 'bitcoin')
    limit = int(request.args.get('limit', 5))
    result = twitter_search(query, limit)
    return jsonify({"query": query, "limit": limit, "result": result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

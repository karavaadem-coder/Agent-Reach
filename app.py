from flask import Flask, request, jsonify
import subprocess
import os
import requests
import re
import json

app = Flask(__name__)

# Telegram Bot Token (Render Environment Variables'dan al)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Twitter Cookie'ler DOĞRUDAN KODDA
TWITTER_AUTH_TOKEN = '52152f0d039da006b688aca40957317b9074207c'
TWITTER_CT0 = '331cc0470c3fd821b940a303fefa2d71a380fc6ee8c279c2fad091192b0aa3c7fc9e6e1c962575af2f7e8abe3f12ce4b20c38c91835c65fffe065b436f2b5cf8ea3fd1cf9700a9a17bbe20e986ffbeef'

@app.route('/')
def home():
    return jsonify({
        "status": "Telegram Twitter + CSS Bot Çalışıyor!",
        "endpoints": {
            "/webhook": "Telegram webhook (POST)",
            "/search": "Twitter arama test (GET)",
            "/css": "CSS analiz test (GET)"
        }
    })

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Telegram'dan gelen mesajları işler"""
    if request.method == 'GET':
        return jsonify({"status": "Webhook adresi çalışıyor. POST isteği bekleniyor."})
    
    try:
        data = request.get_json()
        print(f"📩 Gelen mesaj: {data}")
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            
            if text == '/start':
                send_message(chat_id, """
🤖 **Twitter + CSS Arama Botu'na Hoş Geldin!**

📌 **Komutlar:**
/search [kelime] [sayı] → Tweet ara (örn: /search bitcoin 5)
/css [url] → Web sitesinin CSS bilgilerini topla (örn: /css https://example.com)
/trend → Trend konuları göster
/help → Yardım menüsü
                """)
                return jsonify({"status": "ok"})
            
            if text.startswith('/search'):
                parts = text.split(' ')
                if len(parts) >= 2:
                    query = parts[1]
                    try:
                        limit = int(parts[2]) if len(parts) >= 3 else 5
                    except ValueError:
                        limit = 5
                    send_message(chat_id, f"🔍 `{query}` aranıyor... ⏳")
                    result = twitter_search(query, limit)
                    send_message(chat_id, result)
                else:
                    send_message(chat_id, "❌ Kullanım: `/search kelime sayı`")
            
            elif text.startswith('/css'):
                parts = text.split(' ')
                if len(parts) >= 2:
                    url = parts[1]
                    send_message(chat_id, f"🎨 `{url}` CSS analiz ediliyor... ⏳")
                    result = css_analyzer(url)
                    send_message(chat_id, result)
                else:
                    send_message(chat_id, "❌ Kullanım: `/css https://ornek.com`")
            
            elif text == '/trend':
                send_message(chat_id, "📈 Trend konular aranıyor... ⏳")
                result = twitter_search('trending', 10)
                send_message(chat_id, f"📈 **Trend Konular:**\n{result}")
            
            elif text == '/help':
                send_message(chat_id, """
📖 **Komutlar:**
/search [kelime] [sayı] → Tweet ara
/css [url] → Web sitesi CSS bilgileri
/trend → Trend konular
/help → Bu mesaj
                """)
            else:
                send_message(chat_id, "❌ Bilinmeyen komut. `/help` yaz.")
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"❌ Hata: {e}")
        return jsonify({"error": str(e)}), 500

def twitter_search(query, limit):
    """Twitter araması yapar ve sonucu DETAYLI formatlar"""
    try:
        limit = int(limit)
        os.environ['TWITTER_AUTH_TOKEN'] = TWITTER_AUTH_TOKEN
        os.environ['TWITTER_CT0'] = TWITTER_CT0
        
        cmd = ['twitter', 'search', query, '-n', str(limit), '--format', 'json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            try:
                tweets = json.loads(result.stdout)
                if not tweets:
                    return f"❌ '{query}' için sonuç bulunamadı."
                
                formatted = f"🔍 **'{query}' için {len(tweets[:limit])} tweet:**\n\n"
                for i, tweet in enumerate(tweets[:limit], 1):
                    # Kullanıcı bilgileri
                    username = tweet.get('user', {}).get('screen_name', 'bilinmiyor')
                    name = tweet.get('user', {}).get('name', 'bilinmiyor')
                    text = tweet.get('text', '')[:300]
                    created_at = tweet.get('created_at', 'tarih yok')
                    
                    # Tweet linki
                    tweet_id = tweet.get('id_str', '')
                    tweet_url = f"https://twitter.com/{username}/status/{tweet_id}" if username and tweet_id else ""
                    
                    formatted += f"{i}. **@{username}** ({name})\n"
                    formatted += f"   📝 {text}\n"
                    formatted += f"   📍 {created_at}\n"
                    if tweet_url:
                        formatted += f"   🔗 {tweet_url}\n"
                    formatted += "\n"
                return formatted
            except json.JSONDecodeError:
                # JSON değilse düz metin olarak göster
                return f"🔍 **'{query}' için sonuç:**\n\n{result.stdout[:1500]}"
        else:
            return f"❌ '{query}' için sonuç bulunamadı.\nHata: {result.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return "❌ Zaman aşımı: Twitter çok yavaş yanıt verdi."
    except Exception as e:
        return f"❌ Hata: {str(e)}"

def css_analyzer(url):
    """Web sitesinden CSS verilerini toplar ve analiz eder"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        css_links = re.findall(r'href=[\'"]?([^\'" >]+\.css[^\'" >]*)', html)
        inline_css = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
        
        result = f"🎨 **CSS Analiz Sonuçları:**\n\n"
        result += f"📄 **Sayfa:** {url}\n"
        result += f"📦 **CSS Dosyaları:** {len(css_links)} adet\n"
        result += f"📝 **Inline CSS:** {'Var' if inline_css else 'Yok'}\n\n"
        
        if css_links:
            result += "📁 **CSS Dosyaları (ilk 5):**\n"
            for i, link in enumerate(css_links[:5], 1):
                result += f"{i}. {link[:80]}\n"
        
        if inline_css:
            result += f"\n📝 **Inline CSS Örneği:**\n"
            sample = inline_css[0][:150].replace('\n', ' ').strip()
            result += f"```css\n{sample}...\n```\n"
        
        frameworks = detect_frameworks(html)
        if frameworks:
            result += f"\n🧩 **Tespit Edilen Framework'ler:**\n"
            for fw in frameworks:
                result += f"• {fw}\n"
        
        colors = extract_colors(html)
        if colors:
            result += f"\n🎨 **Renk Paleti (ilk 10):**\n"
            for color in colors[:10]:
                result += f"• {color}\n"
        
        return result
    except Exception as e:
        return f"❌ CSS analiz hatası: {str(e)}"

def detect_frameworks(html):
    frameworks = []
    html_lower = html.lower()
    if 'bootstrap' in html_lower: frameworks.append('Bootstrap')
    if 'tailwind' in html_lower: frameworks.append('Tailwind CSS')
    if 'foundation' in html_lower: frameworks.append('Foundation')
    if 'bulma' in html_lower: frameworks.append('Bulma')
    if 'materialize' in html_lower: frameworks.append('Materialize')
    if 'semantic-ui' in html_lower or 'semantic ui' in html_lower: frameworks.append('Semantic UI')
    if 'uikit' in html_lower: frameworks.append('UIkit')
    return frameworks if frameworks else ["Bilinmiyor/tespit edilemedi"]

def extract_colors(html):
    color_pattern = r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\([^)]+\)|hsl\([^)]+\)'
    colors = re.findall(color_pattern, html)
    unique_colors = list(set(colors))
    return unique_colors[:15]

def send_message(chat_id, text):
    """Telegram'a mesaj gönder"""
    try:
        url = f"{TELEGRAM_URL}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, json=payload)
        print(f"📤 Mesaj gönderildi: {response.status_code}")
    except Exception as e:
        print(f"❌ Mesaj gönderme hatası: {e}")

@app.route('/search', methods=['GET'])
def test_search():
    query = request.args.get('q', 'bitcoin')
    try:
        limit = int(request.args.get('limit', 5))
    except ValueError:
        limit = 5
    result = twitter_search(query, limit)
    return jsonify({"query": query, "limit": limit, "result": result})

@app.route('/css', methods=['GET'])
def test_css():
    url = request.args.get('url', 'https://example.com')
    result = css_analyzer(url)
    return jsonify({"url": url, "result": result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

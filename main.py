from fastapi import FastAPI
from agent_reach import AgentReach
import uvicorn
import os

app = FastAPI()

# Projenin kendi içindeki agent_reach modülünü tetikliyoruz
try:
    reach = AgentReach()
except Exception as e:
    print(f"Agent Reach başlatılamadı: {e}")
    reach = None

@app.get("/")
def home():
    return {"durum": "Agent Reach aktif ve çalışıyor!"}

@app.get("/ara/twitter")
def twitter_ara(q: str, limit: int = 5):
    if not reach:
        return {"hata": "Agent Reach altyapısı yüklenemedi."}
    try:
        tweets = reach.twitter.search(query=q, limit=limit)
        sonuclar = [{"yazar": t.author, "metin": t.text} for t in tweets]
        return {"data": sonuclar}
    except Exception as e:
        return {"hata": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=
                port)

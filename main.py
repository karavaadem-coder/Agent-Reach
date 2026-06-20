from fastapi import FastAPI, Query
import subprocess
import json
import os
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"durum": "Agent Reach CLI Köprüsü Aktif!"}

@app.get("/ara/twitter")
def twitter_ara(q: str = Query(..., description="Aranacak kelime"), limit: int = 5):
    try:
        # Agent Reach'in yeni yapısında komutlar doğrudan terminalden çağrılıyor.
        # twitter-cli aracını q parametresiyle tetikliyoruz.
        command = f"twitter search \"{q}\" --limit {limit}"
        
        # Komutu arka planda çalıştırıp çıktıyı yakalıyoruz
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        if process.returncode != 0:
            return {
                "hata": "Komut çalıştırılırken bir sorun oluştu.",
                "detay": process.stderr.strip()
            }
            
        # Çıktıyı ekrana basıyoruz
        return {
            "sorgu": q,
            "ham_cikti": process.stdout.strip()
        }
        
    except Exception as e:
        return {"hata": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=p
                ort)

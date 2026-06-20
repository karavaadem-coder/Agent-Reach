from fastapi import FastAPI, Query
import subprocess
import os
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"durum": "Agent Reach CLI Köprüsü Aktif!"}

@app.get("/ara/twitter")
def twitter_ara(q: str = Query(..., description="Aranacak kelime"), limit: int = 5):
    try:
        # Doğrudan temiz komutu tetikliyoruz
        command = f"twitter search \"{q}\" --limit {limit}"
        
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        if process.returncode != 0:
            return {
                "hata": "Arka plandaki Twitter CLI aracı bir hata döndürdü.",
                "detay": process.stderr.strip() if process.stderr else process.stdout.strip()
            }
            
        return {
            "sorgu": q,
            "ham_cikti": process.stdout.strip()
        }
        
    except Exception as e:
        return {"hata": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

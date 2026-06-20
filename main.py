from fastapi import FastAPI, Query
import subprocess
import os
import uvicorn
import shutil

app = FastAPI()

@app.get("/")
def home():
    return {"durum": "Agent Reach CLI Köprüsü Aktif!"}

@app.get("/ara/twitter")
def twitter_ara(q: str = Query(..., description="Aranacak kelime"), limit: int = 5):
    try:
        # Docker (nikolaik/python-nodejs) ortamında global npm ve pipx araçları
        # genellikle bu iki yoldan birine yüklenir. İkisini de kontrol edip tam yolu buluyoruz.
        possible_paths = [
            "/usr/local/bin/twitter",
            "/root/.local/bin/twitter",
            "twitter" # Eğer şansımıza PATH'e eklendiyse
        ]
        
        twitter_bin = "twitter"
        for path in possible_paths:
            if os.path.exists(path) or shutil.which(path):
                twitter_bin = path
                break

        # Komutu doğrudan asıl aracı hedef alarak oluşturuyoruz
        command = f"{twitter_bin} search \"{q}\" --limit {limit}"
        
        # Komutu arka planda çalıştırıp çıktıları yakalıyoruz
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # Eğer komut yine de bulunamaz veya hata verirse detayı görelim
        if process.returncode != 0:
            return {
                "hata": "Arka plandaki Twitter CLI aracı yürütülürken hata döndü.",
                "denenen_komut": command,
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

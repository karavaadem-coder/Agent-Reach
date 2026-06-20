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
        # Agent Reach CLI komutunu arka planda tetikliyoruz
        command = f"twitter search \"{q}\" --limit {limit}"
        
        # Komutu çalıştırıp çıktıları yakalıyoruz
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # Eğer komut bulunamazsa veya sistem hatası verirse
        if process.returncode != 0:
            return {
                "hata": "Komut çalıştırılırken bir sorun oluştu veya bağımlılıklar eksik.",
                "detay": process.stderr.strip()
            }
            
        # Başarılı çıktıyı ham metin olarak döndürüyoruz
        return {
            "sorgu": q,
            "ham_cikti": process.stdout.strip()
        }
        
    except Exception as e:
        return {"hata": str(e)}

if __name__ == "__main__":
    # Render'ın dinamik port atamasını yakalar, parantezi eksiksiz kapatır
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

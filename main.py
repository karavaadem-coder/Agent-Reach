from fastapi import FastAPI, Query
import subprocess
import os
import uvicorn
import sys

app = FastAPI()

@app.get("/")
def home():
    return {"durum": "Agent Reach CLI Köprüsü Aktif!"}

@app.get("/ara/twitter")
def twitter_ara(q: str = Query(..., description="Aranacak kelime"), limit: int = 5):
    try:
        # Mevcut python çalıştırıcısının yolunu alıyoruz (Docker içindeki tam yol)
        python_executable = sys.executable
        
        # Sistemi 'twitter' komutu aramak zorunda bırakmıyoruz.
        # Doğrudan agent_reach modülünü python aracılığıyla tetikliyoruz.
        command = f"{python_executable} -m agent_reach twitter search \"{q}\" --limit {limit}"
        
        # Komutu arka planda çalıştırıp çıktıları yakalıyoruz
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # Eğer yine de modül bulunamazsa hatayı detaylıca görelim
        if process.returncode != 0:
            return {
                "hata": "Agent Reach modülü tetiklenirken bir sorun oluştu.",
                "komut_denenen": command,
                "detay": process.stderr.strip() if process.stderr else process.stdout.strip()
            }
            
        # Başarılı çıktıyı döndürüyoruz
        return {
            "sorgu": q,
            "ham_cikti": process.stdout.strip()
        }
        
    except Exception as e:
        return {"hata": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

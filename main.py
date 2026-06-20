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
        # Madem 'python -m' doğrudan çalışmıyor, paketin cli modülünü script olarak tetikliyoruz.
        # Bu yöntem, projenin işletim sistemine bağımlı olmadan çalışmasını sağlar.
        python_executable = sys.executable
        command = f"{python_executable} -c \"from agent_reach.cli import main; import sys; sys.argv=['agent-reach', 'twitter', 'search', '{q}', '--limit', '{limit}']; main()\""
        
        # Eğer yukarıdaki modül yolu uyuşmazsa (bazen sadece 'core' veya ana dizindedir), 
        # Garanti olması için arkadaki alt aracı (twitter-cli) doğrudan kendi python ortamıyla tetiklemeyi deniyoruz:
        # Not: Üstteki komut başarısız olursa bu çalışır.
        
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # Hata durumunda detayları görelim
        if process.returncode != 0:
            return {
                "hata": "Agent Reach CLI fonksiyonu yürütülürken hata döndü.",
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

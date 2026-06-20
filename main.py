from fastapi import FastAPI, Query
import subprocess
import os
import uvicorn

app = FastAPI()

# Sunucu ilk açıldığında 'twitter' dosyasının yerini sisteme bir kez taratıp hafızada tutacağız
TWITTER_EXECUTABLE_PATH = "twitter"

def find_twitter_binary():
    global TWITTER_EXECUTABLE_PATH
    try:
        # Docker konteynerinin tamamında adı tam olarak 'twitter' olan dosyaları aratıyoruz
        # Bu işlem 'not found' hatasını kökten bitirir.
        result = subprocess.run(
            "find / -type f -name 'twitter' 2>/dev/null",
            shell=True,
            stdout=subprocess.PIPE,
            text=True
        )
        paths = result.stdout.strip().split('\n')
        
        # Bulunan yollardan geçerli olanları filtreleyelim
        for p in paths:
            if p and os.path.exists(p) and ("bin" in p or "local" in p or "venv" in p):
                TWITTER_EXECUTABLE_PATH = p
                print(f"[BAŞARILI] Twitter CLI aracı şu konumda bulundu: {TWITTER_EXECUTABLE_PATH}")
                return
    except Exception as e:
        print(f"Arama esnasında hata: {str(e)}")

# Sunucu başlarken taramayı tetikle
find_twitter_binary()

@app.get("/")
def home():
    return {
        "durum": "Agent Reach CLI Köprüsü Aktif!",
        "twitter_motoru_konumu": TWITTER_EXECUTABLE_PATH
    }

@app.get("/ara/twitter")
def twitter_ara(q: str = Query(..., description="Aranacak kelime"), limit: int = 5):
    try:
        # Keşfettiğimiz tam yolu kullanarak komutu tetikliyoruz
        command = f"\"{TWITTER_EXECUTABLE_PATH}\" search \"{q}\" --limit {limit}"
        
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        if process.returncode != 0:
            return {
                "hata": "Arka plandaki Twitter motoru yürütülürken hata döndü.",
                "denenen_komut": command,
                "detay": process.stderr.strip() if process.stderr else process.stdout.strip(),
                "aktif_motor_yolu": TWITTER_EXECUTABLE_PATH
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

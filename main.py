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
        # Docker içinde twitter-cli'ın yüklenebileceği tüm olası gizli yolları tarıyoruz
        # Python'ın kendi site-packages dizinlerini de bu listeye dahil ediyoruz
        possible_bins = [
            "twitter",
            "/usr/local/bin/twitter",
            "/root/.local/bin/twitter",
            "/root/.config/composer/vendor/bin/twitter",
        ]
        
        # Python'ın kurulu paketlerinin binary (bin) dizinlerini de ekleyelim
        for path in sys.path:
            if "site-packages" in path:
                # site-packages'ın bir üst dizininde veya içindeki bin klasöründe olabilir
                base_path = path.split("lib")[0]
                possible_bins.append(os.path.join(base_path, "bin", "twitter"))
                possible_bins.append(os.path.join(path, "agent_reach", "bin", "twitter"))

        # Gerçekten var olan ilk dosyayı seçiyoruz
        twitter_bin = "twitter"
        for bin_path in possible_bins:
            if os.path.exists(bin_path):
                twitter_bin = bin_path
                break

        # Komutu doğrudan asıl dosya yolunu hedef alarak tetikliyoruz
        command = f"{twitter_bin} search \"{q}\" --limit {limit}"
        
        process = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # Eğer hala bulunamadıysa, sistemdeki tüm gizli yolları log olarak dönelim ki görebilelim
        if process.returncode != 0:
            return {
                "hata": "Arka plandaki Twitter motoru tetiklenirken hata oluştu.",
                "denenen_komut": command,
                "detay": process.stderr.strip() if process.stderr else process.stdout.strip(),
                "sistem_yollari": [p for p in possible_bins if os.path.exists(p)]
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

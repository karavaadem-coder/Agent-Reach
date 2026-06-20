# Python ve Node.js'in bir arada olduğu temiz bir Linux imajı seçiyoruz
FROM nikolaik/python-nodejs:python3.10-nodejs22

WORKDIR /app

# Önce bağımlılıkları kopyalayıp yüklüyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projenin tüm dosyalarını içeri alıyoruz
COPY . .

# Agent Reach'i ve arka plandaki tüm CLI araçlarını root yetkisiyle kuruyoruz
RUN pip install .
RUN agent-reach install --env=auto --safe

# Render'ın portunu dışarı açıyoruz
EXPOSE 10000

# Uygulamayı başlatıyoruz
CMD ["python", "main
.py"]

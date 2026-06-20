FROM nikolaik/python-nodejs:python3.10-nodejs22

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore

# Komutların aranacağı tüm sistem yollarını (PATH) çevre değişkeni olarak Docker'a gömüyoruz
ENV PATH="/root/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

# 141 hatası vermeyen, etkileşimli soruları otomatik onaylayan en güvenli Linux yöntemi:
RUN echo "y" | agent-reach install --env=auto --safe || true

EXPOSE 10000

CMD ["python", "main.py"]

FROM nikolaik/python-nodejs:python3.10-nodejs22

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore

# npm ve python global binary yollarını işletim sisteminin hafızasına (PATH) kazıyoruz
ENV PATH="/root/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .
# Tam yetkiyle tüm bağımlılıkları ve twitter-cli gibi araçları kurduruyoruz
RUN agent-reach install --env=auto --safe

EXPOSE 10000

CMD ["python", "main.py"]

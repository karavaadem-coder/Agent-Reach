FROM nikolaik/python-nodejs:python3.10-nodejs22

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .
RUN agent-reach install --env=auto --safe

EXPOSE 10000

CMD ["python", "main.py"]

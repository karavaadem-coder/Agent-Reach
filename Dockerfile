FROM nikolaik/python-nodejs:python3.10-nodejs22

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore
ENV PATH="/root/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

EXPOSE 10000

CMD ["python", "main.py"]

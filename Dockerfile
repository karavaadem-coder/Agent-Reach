FROM nikolaik/python-nodejs:python3.10-nodejs22

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore
ENV PATH="/root/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

# exit 141 hatasını engellemek için pipefail'i geçici olarak esnetiyoruz 
# veya doğrudan sorunsuz çalışan bir alt kabuk döngüsü kullanıyoruz.
RUN bash -c "yes | agent-reach install --env=auto --safe || true"

EXPOSE 10000

CMD ["python", "m
ain.py"]

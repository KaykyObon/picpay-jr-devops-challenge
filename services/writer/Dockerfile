FROM python:3.9@sha256:0279e49430e0c5add713342b275ab6f0e074a11b2f8f57f78429710a91b9d7bc

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x main.py

EXPOSE 8081

ENTRYPOINT ["python", "./main.py"]


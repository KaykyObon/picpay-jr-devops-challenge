FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x main.py

EXPOSE 8081

ENTRYPOINT ["python", "./main.py"]


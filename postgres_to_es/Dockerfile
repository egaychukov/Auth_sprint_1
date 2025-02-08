FROM python:3.13-slim

WORKDIR /postgres_to_es

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["python3", "main.py"]

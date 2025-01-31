FROM python:3.13-slim

WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

WORKDIR /app/src

ENTRYPOINT ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn_worker.UvicornWorker", "-b", "0.0.0.0:8000"]
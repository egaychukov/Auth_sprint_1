FROM python:3.13-slim

WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

WORKDIR /app/src

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
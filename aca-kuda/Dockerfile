FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# No ports exposed; this is a worker, not an HTTP API
CMD ["python", "worker.py"]

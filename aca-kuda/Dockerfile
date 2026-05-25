FROM python:3.11-slim

WORKDIR /app

COPY aca-kuda/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aca-kuda/ .

# No ports exposed; this is a worker, not an HTTP API
CMD ["python", "worker.py"]

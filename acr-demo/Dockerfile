FROM python:3.11-slim
WORKDIR /app
COPY acr-demo/requirements.txt .
RUN pip install -r requirements.txt
COPY acr-demo/ .
EXPOSE 5000
CMD ["python", "app.py"]

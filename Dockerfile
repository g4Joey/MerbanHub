FROM python:3.13.4-slim

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y poppler-utils tesseract-ocr libtesseract-dev curl && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --retries=5 CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "ocr_watcher.py"]

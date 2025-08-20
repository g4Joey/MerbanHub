FROM python:3.13.4-slim

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --retries=5 CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "ocr_watcher.py"]
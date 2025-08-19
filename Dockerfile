FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Tesseract and Poppler for OCR
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils

COPY ocr_watcher.py .
COPY .env .  # If you use environment variables

EXPOSE 8000

CMD ["python", "ocr_watcher.py"]

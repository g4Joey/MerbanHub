
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OCR, image processing, and PDF conversion

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    poppler-utils \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the FastAPI port
EXPOSE 8001

# Add a healthcheck for container robustness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl --fail http://localhost:8001/health || exit 1

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "ocr_watcher:app", "--host", "0.0.0.0", "--port", "8001"]

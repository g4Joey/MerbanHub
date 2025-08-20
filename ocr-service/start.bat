@echo off
REM Create directories
if not exist "incoming-scan" mkdir incoming-scan
if not exist "fully_indexed" mkdir fully_indexed
if not exist "partially_indexed" mkdir partially_indexed
if not exist "failed" mkdir failed
if not exist "logs" mkdir logs

echo Building OCR Watcher microservice...
docker-compose build

echo Starting OCR Watcher microservice...
docker-compose up -d

echo OCR Watcher microservice is now running on http://localhost:8000
echo Health check: curl http://localhost:8000/health
echo Stats: curl http://localhost:8000/stats
echo.
echo To view logs: docker-compose logs -f ocr-watcher
echo To stop: docker-compose down

pause

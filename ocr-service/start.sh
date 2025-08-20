# Create directories
mkdir -p incoming-scan fully_indexed partially_indexed failed logs

# Build and run the OCR Watcher microservice
echo "Building OCR Watcher microservice..."
docker-compose build

echo "Starting OCR Watcher microservice..."
docker-compose up -d

echo "OCR Watcher microservice is now running on http://localhost:8000"
echo "Health check: curl http://localhost:8000/health"
echo "Stats: curl http://localhost:8000/stats"
echo ""
echo "To view logs: docker-compose logs -f ocr-watcher"
echo "To stop: docker-compose down"

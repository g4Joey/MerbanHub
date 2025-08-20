# OCR Watcher Microservice

A containerized microservice for OCR document processing and file watching.

## Features

- **File Watching**: Monitors incoming-scan directory for new documents
- **OCR Processing**: Extracts text from PDFs and images using Tesseract
- **Intelligent Routing**: Automatically categorizes documents based on extracted information
- **REST API**: Provides endpoints for searching and monitoring
- **Health Checks**: Built-in health monitoring for container orchestration
- **Scalable**: Designed for microservice architecture

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f ocr-watcher

# Stop the service
docker-compose down
```

### Using Docker

```bash
# Build the image
docker build -t ocr-watcher .

# Run the container
docker run -d \
  --name ocr-watcher \
  -p 8000:8000 \
  -v $(pwd)/incoming-scan:/app/incoming-scan \
  -v $(pwd)/fully_indexed:/app/fully_indexed \
  -v $(pwd)/partially_indexed:/app/partially_indexed \
  -v $(pwd)/failed:/app/failed \
  ocr-watcher
```

## API Endpoints

- `GET /health` - Health check
- `GET /stats` - Processing statistics
- `GET /search?q=<term>` - Search processed files

## Configuration

Environment variables can be set in `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | API server host |
| `PORT` | `8000` | API server port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `OCR_DPI` | `600` | OCR processing DPI |
| `MAX_RETRIES` | `3` | File operation retries |

## Directory Structure

```
ocr-service/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── requirements.txt        # Python dependencies
├── config.py              # Configuration management
├── ocr_watcher.py         # Main application
├── incoming-scan/         # Input directory (mounted)
├── fully_indexed/         # Fully processed files (mounted)
├── partially_indexed/     # Partially processed files (mounted)
├── failed/               # Failed processing files (mounted)
└── logs/                 # Application logs (mounted)
```

## Monitoring

The service includes:
- Health check endpoint at `/health`
- Structured logging to both file and console
- Docker health checks for container orchestration
- Processing statistics at `/stats`

## Integration

This microservice can be integrated into larger systems through:
- REST API calls
- File system monitoring
- Container orchestration (Kubernetes, Docker Swarm)
- Service mesh integration

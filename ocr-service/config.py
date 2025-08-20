import os
from pathlib import Path

# Environment-based configuration
class Config:
    # OCR Tool Paths (will be different in container)
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', '/usr/bin/tesseract')
    POPPLER_PATH = os.getenv('POPPLER_PATH', '/usr/bin')
    
    # Directories
    SCAN_DIR = os.getenv('SCAN_DIR', 'incoming-scan')
    FULLY_INDEXED_DIR = os.getenv('FULLY_INDEXED_DIR', 'fully_indexed')
    PARTIAL_INDEXED_DIR = os.getenv('PARTIAL_INDEXED_DIR', 'partially_indexed')
    FAILED_DIR = os.getenv('FAILED_DIR', 'failed')
    DEBUG_DIR = os.getenv('DEBUG_DIR', 'debug')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # API Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(LOG_DIR, 'ocr_debug.log')
    
    # OCR Settings
    DPI = int(os.getenv('OCR_DPI', 600))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_DELAY = float(os.getenv('RETRY_DELAY', 1.0))
    
    # File Processing
    BATCH_DELAY = float(os.getenv('BATCH_DELAY', 0.5))
    PROCESS_DELAY = float(os.getenv('PROCESS_DELAY', 5))
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for dir_attr in ['SCAN_DIR', 'FULLY_INDEXED_DIR', 'PARTIAL_INDEXED_DIR', 
                        'FAILED_DIR', 'DEBUG_DIR', 'LOG_DIR']:
            dir_path = getattr(cls, dir_attr)
            Path(dir_path).mkdir(parents=True, exist_ok=True)

# OCR Watcher Setup Guide

This guide will help you set up the OCR Watcher application on your local machine.

## Prerequisites

### 1. System Requirements
- Python 3.8 or higher
- Git
- Windows OS (paths are configured for Windows)

### 2. Install System Dependencies

#### Install Tesseract OCR
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Add to PATH or note the installation path

#### Install Poppler (for PDF processing)
1. Download Poppler for Windows from: https://blog.alivate.com.au/poppler-windows/
2. Extract to: `C:\poppler-24.08.0\`
3. Note the `bin` folder path: `C:\poppler-24.08.0\Library\bin`

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/g4Joey/MerbanHub.git
cd MerbanHub
git checkout kojo-ocr-clean
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Or if using Command Prompt
.venv\Scripts\activate.bat
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure System Paths
Edit `ocr_watcher.py` and update these paths to match your system:

```python
# Update these lines around line 80-82
POPPLER_PATH  = r"C:\poppler-24.08.0\Library\bin"  # Your Poppler path
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Your Tesseract path
```

### 5. Create Environment File
Create a `.env` file in the project root with your database configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
MYSQL_USER=your_database_username
MYSQL_PASSWORD=your_database_password
MYSQL_DATABASE=your_database_name

# Optional: Directory Configuration (uses defaults if not specified)
SCAN_DIR=incoming-scan
FULLY_INDEXED_DIR=fully_indexed
PARTIAL_INDEXED_DIR=partially_indexed
FAILED_DIR=failed
PENDING_DIR=pending
DB_FAILED_DIR=db_failed
```

### 6. Set Up Database (Optional)
If you want to use the database features:
1. Install MySQL/MariaDB
2. Create a database
3. Create the required table:

```sql
CREATE TABLE scanned_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_name VARCHAR(255),
    account_number VARCHAR(100),
    filename VARCHAR(255),
    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. Test the Setup
```bash
# Make sure virtual environment is activated
python ocr_watcher.py
```

You should see:
```
[2025-XX-XX XX:XX:XX] INFO: [WATCHING] /path/to/incoming-scan → (fully|partial|pending|failed)
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Usage

1. **Drop files**: Place PDF or image files in the `incoming-scan` folder
2. **Monitor processing**: Watch the console logs for processing status
3. **Check results**: Processed files will be moved to:
   - `fully_indexed/` - Both name and account extracted with high confidence
   - `partially_indexed/` - One field extracted with high confidence
   - `pending/` - Low confidence extractions
   - `failed/` - No extraction possible

4. **Search API**: Access the search endpoint at `http://localhost:8000/search?q=searchterm`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure virtual environment is activated and dependencies installed
2. **Tesseract not found**: Update `TESSERACT_CMD` path in `ocr_watcher.py`
3. **Poppler not found**: Update `POPPLER_PATH` path in `ocr_watcher.py`
4. **Database connection failed**: Check your `.env` file and database configuration

### Quick Fixes

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python path
where python

# Check if in virtual environment
echo $VIRTUAL_ENV  # Linux/Mac
echo %VIRTUAL_ENV%  # Windows CMD
$env:VIRTUAL_ENV   # Windows PowerShell
```

## File Processing Examples

The system extracts names and account numbers from documents with patterns like:

- `SURNAME : YAMOAH`
- `FIRST NAME : PONKO`
- `OTHER NAMES : AMA`
- `ACCOUNT NUMBER: 1000786423`

Results in filename: `YAMOAH_PONKO_AMA_1000786423.pdf`

Or:

- `CLIENT NAME : AKUA BISSI`
- `ACCOUNT NUMBER: 34007802837`

Results in filename: `AKUA_BISSI_34007802837.pdf`


import os
import time
import shutil
import re
import logging
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from dotenv import load_dotenv
import mysql.connector


load_dotenv()

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# DB Config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", os.getenv("MYSQL_HOST", "localhost")),
    "port": int(os.getenv("DB_PORT", os.getenv("MYSQL_PORT", 3306))),
    "user": os.getenv("DB_USER", os.getenv("MYSQL_USER")),
    "password": os.getenv("DB_PASSWORD", os.getenv("MYSQL_PASSWORD")),
    "database": os.getenv("DB_NAME", os.getenv("MYSQL_DATABASE"))
}


def test_database_connection():
    """
    Test database connection and verify table exists.
    Creates table if it doesn't exist.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test connection
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        # Check if scanned_documents table exists, create if not
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scanned_documents (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                client_name     VARCHAR(255) NOT NULL,
                account_number  VARCHAR(100) NOT NULL,
                filename        VARCHAR(255) NOT NULL UNIQUE,
                filepath        TEXT NOT NULL,
                indexed_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_client_account (client_name, account_number),
                INDEX idx_filename (filename),
                INDEX idx_indexed_at (indexed_at)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info("[DB] Database connection successful and table verified")
        return True
        
    except mysql.connector.Error as err:
        logging.error(f"[DB ERROR] Database connection failed: {err}")
        return False
    except Exception as e:
        logging.error(f"[DB ERROR] Unexpected database error: {e}")
        return False


def insert_metadata_to_db(client_name, account_number, filename, filepath):
    """
    Insert extracted document metadata into the scanned_documents table.
    
    Args:
        client_name (str): Extracted client name (e.g., "JOHN_DOE")
        account_number (str): Extracted account number (e.g., "123456789")
        filename (str): New filename after processing (e.g., "JOHN_DOE_123456789.pdf")
        filepath (str): Full path to the processed file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert into scanned_documents table with proper schema
        cursor.execute("""
            INSERT INTO scanned_documents (client_name, account_number, filename, filepath)
            VALUES (%s, %s, %s, %s)
        """, (client_name, account_number, filename, filepath))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info(f"[DB] Successfully inserted: {client_name}, {account_number} -> {filename}")
        return True
        
    except mysql.connector.Error as err:
        logging.error(f"[DB ERROR] Failed to insert into database: {err}")
        return False
    except Exception as e:
        logging.error(f"[DB ERROR] Unexpected error: {e}")
        return False



# === Retry-safe move ===
def safe_move_file(src, dest, max_retries=3, delay=1):
    for attempt in range(1, max_retries + 1):
        try:
            shutil.move(src, dest)
            return True
        except Exception as e:
            print(f"[RENAME ERROR] Attempt {attempt} failed moving {src} to {dest}: {e}")
            time.sleep(delay)
    print(f"[ALERT] Failed to move {src} to {dest} after {max_retries} attempts.")
    return False


# === Directories (configurable) ===
SCAN_DIR            = os.getenv("SCAN_DIR", "incoming-scan")
FULLY_INDEXED_DIR   = os.getenv("FULLY_INDEXED_DIR", "fully_indexed")
PARTIAL_INDEXED_DIR = os.getenv("PARTIAL_INDEXED_DIR", "partially_indexed")
FAILED_DIR          = os.getenv("FAILED_DIR", "failed")
PENDING_DIR         = os.getenv("PENDING_DIR", "pending")
DB_FAILED_DIR       = os.getenv("DB_FAILED_DIR", "db_failed")

# Ensure directories exist
for d in (FULLY_INDEXED_DIR, PARTIAL_INDEXED_DIR, FAILED_DIR, PENDING_DIR, DB_FAILED_DIR):
    os.makedirs(d, exist_ok=True)

# === OCR Tools ===
POPPLER_PATH  = r"C:\poppler-24.08.0\Library\bin"
TESSERACT_CMD = r"C:\Users\KC-User\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
CONFIDENCE_THRESHOLD = 50 # Reasonable threshold for OCR - not too strict, not too lenient

# === OCR & Parsing ===
def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            pages = convert_from_path(path, poppler_path=POPPLER_PATH)
            return "".join(pytesseract.image_to_string(p) for p in pages)
        else:
            img = Image.open(path).convert("RGB")
            return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[ERROR] Text extraction failed for {path}: {e}")
        return ""

def parse_fields_with_confidence(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            pages = convert_from_path(path, poppler_path=POPPLER_PATH)
            ocr_results = [pytesseract.image_to_data(p, output_type=pytesseract.Output.DICT) for p in pages]
        else:
            img = Image.open(path).convert("RGB")
            ocr_results = [pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)]
    except Exception as e:
        print(f"[ERROR] OCR with confidence failed: {e}")
        return None, None, 0, 0

    # Build full text from OCR results
    full_text = ""
    for result in ocr_results:
        full_text += " ".join(result["text"]) + " "
    
    # Debug: Print extracted text to understand what OCR is seeing
    logging.info(f"[DEBUG] OCR Text: {full_text[:200]}...")  # First 200 characters

    # Account number patterns
    account_patterns = [
        r"ACCOUNT\s*NUMBER\s*[:\-]?\s*([A-Za-z0-9\-]+)",
        r"Account\s*Number\s*[:\-]?\s*([A-Za-z0-9\-]+)",
        r"Account\s*no\.?\s*[:\-]?\s*([A-Za-z0-9\-]+)",
        r"Client\s*CSD\s*Securities\s*Account\s*No\s*[:\-]?\s*([A-Za-z0-9\-]+)"
    ]
    
    # Name patterns - updated to handle all the variations we see in the OCR text
    surname_pattern = r"SURNAME\s*[:\-]?\s*([A-Za-z]+)"
    first_name_pattern = r"FIRST\s*NAME\s*[:\-]?\s*([A-Za-z]+)"
    other_names_pattern = r"OTHER\s*NAMES?\s*[:\-]?\s*([A-Za-z]+)"  # Fixed: removed \s to get single word
    client_name_pattern = r"CLIENT\s*NAME\s*[:\-]?\s*([A-Za-z\s]+?)(?=\s+ACCOUNT|$)"  # Fixed: better stopping condition
    general_name_pattern = r"(?<!CLIENT\s)(?<!FIRST\s)NAME\s*[:\-]?\s*([A-Za-z\s]+?)(?=\s+ACCOUNT|$)"  # Added: for general NAME field

    # Extract account number
    account = None
    acc_conf = 0
    for pattern in account_patterns:
        acc_match = re.search(pattern, full_text, re.IGNORECASE)
        if acc_match:
            account = acc_match.group(1).strip()
            acc_conf = extract_confidence_for_text(account, ocr_results)
            break

    # Extract name - try individual fields first, then client name, then general name
    name = None
    name_conf = 0
    
    # Try to extract SURNAME, FIRST NAME, OTHER NAMES
    surname_match = re.search(surname_pattern, full_text, re.IGNORECASE)
    first_name_match = re.search(first_name_pattern, full_text, re.IGNORECASE)
    other_names_match = re.search(other_names_pattern, full_text, re.IGNORECASE)
    
    if surname_match or first_name_match or other_names_match:
        # Build name from individual components
        name_parts = []
        confidences = []
        
        if surname_match:
            surname = surname_match.group(1).strip()
            name_parts.append(surname)
            confidences.append(extract_confidence_for_text(surname, ocr_results))
            
        if first_name_match:
            first_name = first_name_match.group(1).strip()
            name_parts.append(first_name)
            confidences.append(extract_confidence_for_text(first_name, ocr_results))
            
        if other_names_match:
            other_names = other_names_match.group(1).strip()
            name_parts.append(other_names)
            confidences.append(extract_confidence_for_text(other_names, ocr_results))
        
        name = "_".join(name_parts)
        name_conf = min(confidences) if confidences else 0
        
    else:
        # Try CLIENT NAME pattern
        client_name_match = re.search(client_name_pattern, full_text, re.IGNORECASE)
        if client_name_match:
            client_name = client_name_match.group(1).strip()
            name_parts = [part.strip() for part in client_name.split() if part.strip()]
            name = "_".join(name_parts)
            name_conf = extract_confidence_for_text(client_name, ocr_results)
        else:
            # Fall back to general NAME pattern (for SAMPLE1 & SAMPLE2)
            general_name_match = re.search(general_name_pattern, full_text, re.IGNORECASE)
            if general_name_match:
                general_name = general_name_match.group(1).strip()
                name_parts = [part.strip() for part in general_name.split() if part.strip()]
                name = "_".join(name_parts)
                name_conf = extract_confidence_for_text(general_name, ocr_results)

    return name, account, name_conf, acc_conf

def extract_confidence_for_text(target_text, ocr_results):
    """Extract confidence score for a specific text from OCR results"""
    if not target_text:
        return 0
    
    confidences = []
    target_words = target_text.lower().split()
    
    for result in ocr_results:
        words = result["text"]
        confs = result["conf"]
        
        for word, conf in zip(words, confs):
            if conf != "-1" and word.strip():
                for target_word in target_words:
                    if target_word in word.lower():
                        confidences.append(int(conf))
    
    return min(confidences) if confidences else 0

# === Routing ===
def route_file(path):
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()
    is_image = ext in [".png", ".jpg", ".jpeg"]

    name, account, name_conf, acc_conf = parse_fields_with_confidence(path)
    
    # Debug logging to see what we extracted and confidence scores
    logging.info(f"[DEBUG] File: {filename}")
    logging.info(f"[DEBUG] Name: '{name}' (confidence: {name_conf})")
    logging.info(f"[DEBUG] Account: '{account}' (confidence: {acc_conf})")
    logging.info(f"[DEBUG] Threshold: {CONFIDENCE_THRESHOLD}")

    # Determine destination and filename based on extraction success and confidence
    if name and account and name_conf >= CONFIDENCE_THRESHOLD and acc_conf >= CONFIDENCE_THRESHOLD:
        dest_dir = FULLY_INDEXED_DIR
        # Always combine name and account: "NAME_ACCOUNT"
        new_name = f"{name}_{account}.pdf" if is_image else f"{name}_{account}{ext}"
    elif (name and name_conf >= CONFIDENCE_THRESHOLD) or (account and acc_conf >= CONFIDENCE_THRESHOLD):
        dest_dir = PARTIAL_INDEXED_DIR
        # Use whichever field was extracted with high confidence
        if name and account:
            # Both extracted but one has low confidence
            new_name = f"{name}_{account}.pdf" if is_image else f"{name}_{account}{ext}"
        else:
            # Only one field extracted with high confidence
            key = name if name and name_conf >= CONFIDENCE_THRESHOLD else account
            new_name = f"{key}.pdf" if is_image else f"{key}{ext}"
    elif name or account:
        dest_dir = PENDING_DIR
        # Low confidence extraction
        if name and account:
            new_name = f"{name}_{account}.pdf" if is_image else f"{name}_{account}{ext}"
        else:
            key = name or account
            new_name = f"{key}.pdf" if is_image else f"{key}{ext}"
    else:
        dest_dir = FAILED_DIR
        new_name = filename

    dest_path = os.path.join(dest_dir, new_name)
    base, extn = os.path.splitext(new_name)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_dir, f"{base}_{counter}{extn}")
        counter += 1

    file_moved = False
    if is_image and dest_dir != FAILED_DIR:
        try:
            img = Image.open(path).convert("RGB")
            img.save(dest_path, "PDF", resolution=100.0)
            if os.path.exists(path):
                os.remove(path)
            logging.info(f"[{dest_dir.upper()}] {filename} → {new_name} (converted to PDF)")
            file_moved = True
        except Exception as e:
            logging.error(f"[ERROR] PDF conversion failed: {e}")
            fallback = os.path.join(FAILED_DIR, filename)
            safe_move_file(path, fallback)
            logging.error(f"[FAILED] {filename} → {filename}")
    else:
        if safe_move_file(path, dest_path):
            logging.info(f"[{dest_dir.upper()}] {filename} → {new_name}")
            file_moved = True

    # After successful save/move, insert into DB if both name and account exist
    if file_moved and dest_dir in [FULLY_INDEXED_DIR, PARTIAL_INDEXED_DIR] and name and account:
        # Only attempt database insertion if we have valid database config
        if all([DB_CONFIG["user"], DB_CONFIG["password"], DB_CONFIG["database"]]):
            success = insert_metadata_to_db(
                client_name=name,
                account_number=account,
                filename=os.path.basename(dest_path),
                filepath=os.path.abspath(dest_path)
            )
            if not success:
                # Move file to DB_FAILED_DIR for later recovery
                db_failed_path = os.path.join(DB_FAILED_DIR, os.path.basename(dest_path))
                safe_move_file(dest_path, db_failed_path)
                logging.error(f"[DB_FAILED] {os.path.basename(dest_path)} moved to {DB_FAILED_DIR}")
        else:
            logging.warning(f"[DB] Database not configured - skipping DB insertion for {os.path.basename(dest_path)}")



# === Watcher ===
class ScanHandler(FileSystemEventHandler):
    _lock = threading.Lock()
    _timer = None

    def _delayed_batch_process(self):
        with self._lock:
            ScanHandler._timer = None
        time.sleep(5)
        files = [f for f in os.listdir(SCAN_DIR) if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))]
        for f in files:
            path = os.path.join(SCAN_DIR, f)
            if os.path.isfile(path):
                for _ in range(5):
                    try:
                        with open(path, "rb") as t:
                            t.read(1)
                        route_file(path)
                        break
                    except Exception as e:
                        logging.warning(f"[BATCH] File {path} not ready: {e}")
                        time.sleep(0.5)

    def _schedule_batch(self):
        with self._lock:
            if ScanHandler._timer:
                ScanHandler._timer.cancel()
            ScanHandler._timer = threading.Timer(0.5, self._delayed_batch_process)
            ScanHandler._timer.start()

    def on_created(self, event): self._schedule_batch() if not event.is_directory else None
    def on_moved(self, event): self._schedule_batch() if not event.is_directory else None

def start_watcher():
    os.makedirs(SCAN_DIR, exist_ok=True)
    logging.info(f"[WATCHING] {os.path.abspath(SCAN_DIR)} → (fully|partial|pending|failed)")
    obs = Observer()
    obs.schedule(ScanHandler(), SCAN_DIR, recursive=False)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

# === FastAPI Search API ===
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

@app.get("/search")
def search_files(q: str = Query(..., min_length=1)):
    results = []
    for folder, label in [
        (FULLY_INDEXED_DIR, "fully_indexed"),
        (PARTIAL_INDEXED_DIR, "partially_indexed"),
        (PENDING_DIR, "pending")
    ]:
        for fname in os.listdir(folder):
            if q.lower() in fname.lower():
                results.append({
                    "filename": fname,
                    "status": label,
                    "path": os.path.join(folder, fname)
                })
    return {"results": results}

def main():
    """
    Main function to start the OCR watcher and FastAPI server.
    Tests database connection before starting services.
    """
    logging.info("[STARTUP] Starting MerbanHub OCR Watcher...")
    
    # Test database connection
    if not test_database_connection():
        logging.warning("[STARTUP] Database connection failed - continuing without database features")
        logging.warning("[STARTUP] Files will be processed but not stored in database")
    
    # Start file watcher in background thread
    threading.Thread(target=start_watcher, daemon=True).start()
    
    # Start FastAPI server
    logging.info("[STARTUP] Starting API server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

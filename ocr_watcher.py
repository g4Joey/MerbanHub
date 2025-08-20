import os
import time
import shutil
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import numpy as np
import cv2
import logging

# Configure logging
logging.basicConfig(filename='ocr_debug.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

<<<<<<< HEAD
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
=======
# === Retry-safe file move ===
>>>>>>> dev
def safe_move_file(src, dest, max_retries=3, delay=1):
    for attempt in range(1, max_retries + 1):
        try:
            if not os.path.exists(src):
                logging.error(f"Source file {src} does not exist at move attempt {attempt}.")
                return False
            shutil.move(src, dest)
            return True
        except Exception as e:
            logging.error(f"Attempt {attempt} failed moving {src} to {dest}: {e}")
            time.sleep(delay)
    logging.warning(f"Failed to move {src} to {dest} after {max_retries} attempts.")
    return False

# === Directories ===
SCAN_DIR            = "incoming-scan"
FULLY_INDEXED_DIR   = "fully_indexed"
PARTIAL_INDEXED_DIR = "partially_indexed"
FAILED_DIR          = "failed"
DEBUG_DIR          = "debug"

# Ensure directories exist
for d in (FULLY_INDEXED_DIR, PARTIAL_INDEXED_DIR, FAILED_DIR, DEBUG_DIR):
    os.makedirs(d, exist_ok=True)

# === OCR Tools Paths ===
POPPLER_PATH  = r"C:\poppler-24.08.0\Library\bin"
TESSERACT_CMD = r"C:\Users\KC-User\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
<<<<<<< HEAD
CONFIDENCE_THRESHOLD = 50 # Reasonable threshold for OCR - not too strict, not too lenient
=======
>>>>>>> dev

# === OCR & Parsing ===
def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            pages = convert_from_path(path, poppler_path=POPPLER_PATH, dpi=600)
            return "\n".join(pytesseract.image_to_string(p) for p in pages)
        else:
            img = Image.open(path).convert("RGB")
            return pytesseract.image_to_string(img)
    except Exception as e:
        logging.error(f"Text extraction failed for {path}: {e}")
        return ""

def normalize(val):
    # Lowercase, remove underscores, spaces, punctuation
    return re.sub(r'[^a-z0-9]', '', val.lower())

<<<<<<< HEAD
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
=======
def parse_fields(text, img_path=None):
    # All possible labels (case-insensitive, with/without colon, underscore, etc.)
    labels = [
        "Name of Account Holder", "First name", "First names", "Surname", "Surnames",
        "Other name", "Other names", "Print name", "Account Name", "Institution Name",
        "Account Number", "Account number", "Account no", "CSD Number", "Client CSD Securities Account No",
        "ID number", "UMB-IHL ID Number", "Name", "Name of Organisation", "Name of Organization"
    ]
    label_norms = set([normalize(l) for l in labels])
    # Build regex for label matching (with/without colon, case-insensitive)
    label_regex = re.compile(rf"({'|'.join([re.escape(l) for l in labels])})\s*:?", re.IGNORECASE)

    # Strong blacklist: all label variants, generic words, and normalized forms
    blacklist = set(label_norms)
    blacklist.update([normalize(x) for x in [
        "Branch", "Account", "Name", "Surname", "Other", "Print", "Institution", "Organization", "Organisation", "No", "Number", "Holder", "CSD", "ID", "Client", "Details", "Purpose", "Period", "Address", "Tel", "E-Mail", "PHOTO", "Reference", "Date", "Relationship", "Employer", "Spouse", "Failed", "Partial", "Indexed", "Fully", "Of", "The", "And", "Or", "As", "It", "Is", "Are", "Was", "Be", "On", "In", "At", "To", "For", "By", "With", "From", "This", "That", "These", "Those", "A", "An", "PDF", "JPG", "PNG", "Doc", "File", "Scan", "Image", "Document", "Page", "Test", "Sample", "Unknown", "Unnamed", "Blank", "Empty", "None", "Null", "Untitled", "Failed", "Partial", "Indexed", "Fully", "Of", "The", "And", "Or", "As", "It", "Is", "Are", "Was", "Be", "On", "In", "At", "To", "For", "By", "With", "From", "This", "That", "These", "Those", "A", "An"]])

    # If image path is provided, use color info to prefer blue/ink values
    color_data = None
    if img_path:
        img = Image.open(img_path).convert("RGB")
        arr = np.array(img)
        color_data = arr
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
>>>>>>> dev
    else:
        ocr_data = None
    # Split text into lines for context
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        match = label_regex.search(line)
        if match:
            label = match.group(1)
            after_label = line[match.end():].strip()
            # If value is on same line, try to extract all words after label up to next label or end
            value_words = []
            for word in after_label.split():
                nword = normalize(word)
                if nword in label_norms or nword in blacklist:
                    break
                value_words.append(word)
            # If not found, check next line(s) for value
            if not value_words and idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
                for word in next_line.split():
                    nword = normalize(word)
                    if nword in label_norms or nword in blacklist:
                        break
                    value_words.append(word)
            # Join all value words
            value = " ".join(value_words).strip()
            # If color_data is available, prefer blue/ink words (optional, simple heuristic)
            if ocr_data is not None and value:
                for i, w in enumerate(ocr_data["text"]):
                    if normalize(w) == normalize(value):
                        conf = ocr_data["conf"][i]
                        logging.debug(f"OCR confidence for '{w}': {conf}")
                        x, y, w_, h_ = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                        roi = color_data[y:y+h_, x:x+w_]
                        avg_color = np.mean(roi, axis=(0, 1))
                        # Heuristic: blue ink is likely if blue channel is dominant
                        if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:
                            logging.debug(f"Matched label '{label}' (blue/ink) in line: '{line}' -> Value: '{value}'")
                            break
                else:
                    logging.debug(f"Matched label '{label}' in line: '{line}' -> Value: '{value}' (not blue/ink)")
            else:
                logging.debug(f"Matched label '{label}' in line: '{line}' -> Value: '{value}'")
            # Final validation: value must not be empty, must not be a label, must not be in blacklist
            nval = normalize(value)
            if value and nval not in blacklist and len(nval) > 2:
                return value, label
            else:
                logging.debug(f"Value '{value}' rejected by blacklist or is empty.")
    # If nothing valid found, fail
    logging.debug("No valid value found for any label. Failing job.")
    return None, None

def is_valid_account(val):
    # Only accept if at least 10 digits, and mostly 13 digits
    digits = ''.join([c for c in val if c.isdigit()])
    return len(digits) >= 10 and (len(digits) == 13 or len(digits) >= 10)

# === Routing Logic ===
def route_file(src_path):
    logging.info(f"Starting to route file: {src_path}")
    filename = os.path.basename(src_path)
    ext = os.path.splitext(filename)[1].lower()
    logging.info(f"Processing file: {filename}, extension: {ext}")
    text = extract_text(src_path)
    logging.info(f"Extracted text length: {len(text)} characters")
    name, name_label = parse_fields(text, src_path)
    account, account_label = None, None
    # Try to extract account number if not already found as name
    account_labels = [
        "Account Number", "Account number", "Account no", "CSD Number", "Client CSD Securities Account No", "ID number", "UMB-IHL ID Number"
    ]
    # Blacklist from parse_fields
    labels = [
        "Name of Account Holder", "First name", "First names", "Surname", "Surnames",
        "Other name", "Other names", "Print name", "Account Name", "Institution Name",
        "Account Number", "Account number", "Account no", "CSD Number", "Client CSD Securities Account No",
        "ID number", "UMB-IHL ID Number", "Name", "Name of Organisation", "Name of Organization"
    ]
    label_norms = set([normalize(l) for l in labels])
    blacklist = set(label_norms)
    for label in account_labels:
        regex = re.compile(rf"{re.escape(label)}\s*:?\s*([A-Za-z0-9\-]+)", re.IGNORECASE)
        for line in text.splitlines():
            m = regex.search(line)
            if m:
                val = m.group(1).strip()
                nval = normalize(val)
                if val and nval not in blacklist and len(nval) > 2 and is_valid_account(val):
                    account = val
                    account_label = label
                    logging.debug(f"Account candidate '{val}' from label '{label}' accepted as valid account number.")
                    break
                else:
                    logging.debug(f"Account candidate '{val}' from label '{label}' rejected (blacklist or not valid account number).")
        if account:
            break
    # Only fail if both name and account are missing
    if not name and not account:
        logging.error(f"{filename} → {filename} (No valid name or account number found)")
        dest_path = os.path.join(FAILED_DIR, filename)
        safe_move_file(src_path, dest_path)
        return
    is_image = ext in [".png", ".jpg", ".jpeg"]
    if name and account:
        safe_name = re.sub(r'[\\/:*?"<>|]', '', name)
        safe_account = re.sub(r'[\\/:*?"<>|]', '', account)
        new_filename = f"{safe_name}_{safe_account}.pdf" if is_image else f"{safe_name}_{safe_account}{ext}"
        dest_dir = FULLY_INDEXED_DIR
    elif name or account:
        key = name or account
        safe_key = re.sub(r'[\\/:*?"<>|]', '', key)
        new_filename = f"{safe_key}.pdf" if is_image else f"{safe_key}{ext}"
        dest_dir = PARTIAL_INDEXED_DIR
    else:
        # This should not be reached, but fallback to failed
        new_filename = filename
        dest_dir = FAILED_DIR
    dest_path = os.path.join(dest_dir, new_filename)
    base, extn = os.path.splitext(new_filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_dir, f"{base}_{counter}{extn}")
        counter += 1
<<<<<<< HEAD

    file_moved = False
    if is_image and dest_dir != FAILED_DIR:
=======
    if dest_dir == FAILED_DIR:
        if safe_move_file(src_path, dest_path):
            logging.info(f"[{dest_dir.upper()}] {filename} → {new_filename}")
        return
    if is_image:
>>>>>>> dev
        try:
            img = Image.open(src_path).convert("RGB")
            img.save(dest_path, "PDF", resolution=100.0)
            if os.path.exists(src_path):
                os.remove(src_path)
            logging.info(f"[{dest_dir.upper()}] {filename} → {new_filename} (converted to PDF)")
        except Exception as e:
            logging.error(f"Failed to convert {filename} to PDF: {e}")
            if os.path.exists(src_path):
                fallback = os.path.join(FAILED_DIR, filename)
                safe_move_file(src_path, fallback)
                logging.info(f"[FAILED] {filename} → {filename}")
    else:
        if safe_move_file(src_path, dest_path):
            logging.info(f"[{dest_dir.upper()}] {filename} → {new_filename}")

<<<<<<< HEAD
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
=======
# === Watcher Handler ===
>>>>>>> dev
class ScanHandler(FileSystemEventHandler):
    _lock = threading.Lock()
    _timer = None

    def _delayed_batch_process(self):
        with self._lock:
            ScanHandler._timer = None
        logging.info("Starting delayed batch process...")
        time.sleep(5)
        files = [f for f in os.listdir(SCAN_DIR) if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))]
        logging.info(f"Found {len(files)} files to process: {files}")
        for fname in files:
            fpath = os.path.join(SCAN_DIR, fname)
            logging.info(f"Processing file: {fpath}")
            if not os.path.isfile(fpath):
                logging.warning(f"File {fpath} is not a file, skipping")
                continue
            for attempt in range(10):
                try:
                    if not os.path.isfile(fpath):
                        logging.warning(f"File {fpath} no longer exists at attempt {attempt}")
                        break
                    with open(fpath, 'rb') as f:
                        f.read(1)
                    logging.info(f"Routing file: {fpath}")
                    route_file(fpath)
                    logging.info(f"Successfully processed: {fpath}")
                    break
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1} failed for {fpath}: {e}")
                    time.sleep(0.5)
            else:
                logging.error(f"Failed to process {fpath} after multiple attempts.")

    def _schedule_batch(self):
        with self._lock:
            if ScanHandler._timer is not None:
                ScanHandler._timer.cancel()
            ScanHandler._timer = threading.Timer(0.5, self._delayed_batch_process)
            ScanHandler._timer.start()

    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"File created: {event.src_path}")
            self._schedule_batch()

    def on_moved(self, event):
        if not event.is_directory:
            logging.info(f"File moved: {event.src_path}")
            self._schedule_batch()

def start_watcher():
    abs_path = os.path.abspath(SCAN_DIR)
    logging.info(f"[WATCHING] {abs_path} → (fully|partial|failed)")
    os.makedirs(SCAN_DIR, exist_ok=True)
    
    # Process existing files on startup
    existing_files = [f for f in os.listdir(SCAN_DIR) if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))]
    if existing_files:
        logging.info(f"Processing {len(existing_files)} existing files on startup: {existing_files}")
        for fname in existing_files:
            fpath = os.path.join(SCAN_DIR, fname)
            if os.path.isfile(fpath):
                try:
                    logging.info(f"Processing existing file: {fpath}")
                    route_file(fpath)
                    logging.info(f"Successfully processed existing file: {fpath}")
                except Exception as e:
                    logging.error(f"Failed to process existing file {fpath}: {e}")
    
    obs = Observer()
    obs.schedule(ScanHandler(), path=SCAN_DIR, recursive=False)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

<<<<<<< HEAD
# === FastAPI Search API ===
from fastapi import FastAPI, Query, UploadFile, File
=======
from fastapi import FastAPI, Query
>>>>>>> dev
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ─── Insert the FastAPI “app” definition and /search route here ───
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/search")
def search_files(q: str = Query(..., min_length=1)):
    results = []
    for folder, status in [
        (FULLY_INDEXED_DIR,   "fully_indexed"),
        (PARTIAL_INDEXED_DIR, "partially_indexed"),
    ]:
        for fname in os.listdir(folder):
            if q.lower() in fname.lower():
                results.append({
                    "filename": fname,
                    "status": status,
                    "path": os.path.join(folder, fname)
                })
    return {"results": results}

<<<<<<< HEAD
# --- Upload Endpoint ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the incoming-scan directory for OCR processing.
    """
    upload_dir = SCAN_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"success": True, "filename": file.filename, "path": file_path}

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
=======
@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()
>>>>>>> dev
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()


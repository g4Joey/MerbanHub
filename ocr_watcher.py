
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
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}


def insert_metadata_to_db(client_name, account_number, filename, filepath):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scanned_documents (client_name, account_number, filename, filepath)
            VALUES (%s, %s, %s, %s)
        """, (client_name, account_number, filename, filepath))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"[DB] Inserted: {client_name}, {account_number}")
        return True
    except mysql.connector.Error as err:
        logging.error(f"[DB ERROR] Failed to insert into DB: {err}")
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
CONFIDENCE_THRESHOLD = 99

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

    name_labels = [
        r"Name of Account Holder\s*\(corporate entities\)", r"Print name",
        r"Other names?", r"Other name", r"First names?", r"First name",
        r"Surname\s*\(individual\)", r"Surnames", r"Name"
    ]
    account_labels = [
        r"Client CSD Securities Account No", r"Account Number",
        r"Account number", r"Account no", r"Account no\."
    ]
    name_pattern = re.compile(rf"(?:{'|'.join(name_labels)})\s*[:\-]?\s*([A-Za-z ]+)", re.IGNORECASE)
    acc_pattern  = re.compile(rf"(?:{'|'.join(account_labels)})\s*[:\-]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE)

    full_text = ""
    for result in ocr_results:
        full_text += " ".join(result["text"]) + " "

    name_match = name_pattern.search(full_text)
    acc_match = acc_pattern.search(full_text)

    name = name_match.group(1).strip().replace(" ", "_") if name_match else None
    account = acc_match.group(1).strip() if acc_match else None

    def extract_confidence(target):
        if not target:
            return 0
        for result in ocr_results:
            words = result["text"]
            confs = result["conf"]
            for word, conf in zip(words, confs):
                if target.lower() in word.lower() and conf != "-1":
                    return int(conf)
        return 0

    name_conf = extract_confidence(name)
    acc_conf  = extract_confidence(account)

    return name, account, name_conf, acc_conf

# === Routing ===
def route_file(path):
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()
    is_image = ext in [".png", ".jpg", ".jpeg"]

    name, account, name_conf, acc_conf = parse_fields_with_confidence(path)

    if name and account and name_conf >= CONFIDENCE_THRESHOLD and acc_conf >= CONFIDENCE_THRESHOLD:
        dest_dir = FULLY_INDEXED_DIR
        new_name = f"{name}_{account}.pdf" if is_image else f"{name}_{account}{ext}"
    elif (name and name_conf >= CONFIDENCE_THRESHOLD) or (account and acc_conf >= CONFIDENCE_THRESHOLD):
        dest_dir = PARTIAL_INDEXED_DIR
        key = name if name and name_conf >= CONFIDENCE_THRESHOLD else account
        new_name = f"{key}.pdf" if is_image else f"{key}{ext}"
    elif name or account:
        dest_dir = PENDING_DIR
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
    threading.Thread(target=start_watcher, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

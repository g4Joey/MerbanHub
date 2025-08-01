import os
import time
import shutil
import re
import threading
import requests

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
import pytesseract

# Try importing PDF support; if missing, script will still handle images
try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

# ─── Configuration ────────────────────────────────────────────────────────────

# Base folder for this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folders to watch & route into
SCAN_DIR            = os.path.join(BASE_DIR, "incoming-scan")
FULLY_INDEXED_DIR   = os.path.join(BASE_DIR, "fully_indexed")
PARTIAL_INDEXED_DIR = os.path.join(BASE_DIR, "partially_indexed")
FAILED_DIR          = os.path.join(BASE_DIR, "failed")

# Backend endpoint for uploads
BACKEND_UPLOAD_URL = "http://localhost:8080/api/files/upload"

# Optional env‑override for tesseract & poppler
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
POPPLER_PATH  = os.getenv("POPPLER_PATH")

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Ensure folders exist
for d in (SCAN_DIR, FULLY_INDEXED_DIR, PARTIAL_INDEXED_DIR, FAILED_DIR):
    os.makedirs(d, exist_ok=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf" and convert_from_path:
        pages = convert_from_path(path, poppler_path=POPPLER_PATH)
        return "".join(pytesseract.image_to_string(p) for p in pages)
    else:
        img = Image.open(path).convert("RGB")
        return pytesseract.image_to_string(img)

def parse_fields(text: str):
    m_name    = re.search(r"name\s*[:\-]\s*([A-Za-z ]+)", text, re.IGNORECASE)
    m_account = re.search(r"account\s*no\s*[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    name    = m_name.group(1).strip().replace(" ", "_") if m_name else None
    account = m_account.group(1).strip()                if m_account else None
    return name, account

def upload_to_backend(file_path: str):
    try:
        with open(file_path, "rb") as f:
            files = {'file': (os.path.basename(file_path), f)}
            resp = requests.post(BACKEND_UPLOAD_URL, files=files, timeout=10)
            print(f"[UPLOAD] {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Upload failed for {file_path}: {e}")

def route_file(src_path: str):
    filename = os.path.basename(src_path)
    ext = os.path.splitext(filename)[1].lower()

    # 1) Extract & parse
    text = extract_text(src_path)
    name, account = parse_fields(text)

    # 2) Decide new filename & folder
    is_image = ext in [".png", ".jpg", ".jpeg"]
    if name and account:
        key = f"{name}_{account}"
        dest_dir = FULLY_INDEXED_DIR
    elif name or account:
        key = name or account
        dest_dir = PARTIAL_INDEXED_DIR
    else:
        key = filename.rsplit(".",1)[0]
        dest_dir = FAILED_DIR

    new_ext = ".pdf" if is_image else ext
    new_filename = f"{key}{new_ext}"

    # 3) Ensure unique filename
    dest_path = os.path.join(dest_dir, new_filename)
    base, extn = os.path.splitext(new_filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_dir, f"{base}_{counter}{extn}")
        counter += 1

    # 4) Move or convert
    try:
        if dest_dir == FAILED_DIR:
            shutil.move(src_path, dest_path)
        elif is_image:
            img = Image.open(src_path).convert("RGB")
            img.save(dest_path, "PDF", resolution=100.0)
            os.remove(src_path)
        else:
            shutil.move(src_path, dest_path)
        print(f"[{os.path.basename(dest_dir).upper()}] {filename} → {os.path.basename(dest_path)}")
    except Exception as e:
        print(f"[ERROR] Routing failed for {filename}: {e}")
        return

    # 5) Upload to backend
    upload_to_backend(dest_path)

# ─── Watcher ──────────────────────────────────────────────────────────────────

class ScanHandler(FileSystemEventHandler):
    _lock = threading.Lock()
    _timer = None

    def _process_batch(self):
        with self._lock:
            ScanHandler._timer = None
        time.sleep(2)  # debounce
        for fname in os.listdir(SCAN_DIR):
            if not fname.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
                continue
            fpath = os.path.join(SCAN_DIR, fname)
            if not os.path.isfile(fpath):
                continue
            # retry logic
            for _ in range(5):
                try:
                    route_file(fpath)
                    break
                except Exception:
                    time.sleep(0.5)

    def _schedule(self):
        with self._lock:
            if ScanHandler._timer:
                ScanHandler._timer.cancel()
            ScanHandler._timer = threading.Timer(0.5, self._process_batch)
            ScanHandler._timer.start()

    def on_created(self, event):
        if not event.is_directory:
            self._schedule()

    def on_moved(self, event):
        if not event.is_directory:
            self._schedule()

# ─── Main ─────────────────────────────────────────────────────────────────────

def start_watcher():
    print(f"[WATCHING] {SCAN_DIR}")
    obs = Observer()
    obs.schedule(ScanHandler(), path=SCAN_DIR, recursive=False)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    start_watcher()

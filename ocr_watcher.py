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

# === Retry-safe file move ===
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

# === Directories ===
SCAN_DIR            = "incoming-scan"
FULLY_INDEXED_DIR   = "fully_indexed"
PARTIAL_INDEXED_DIR = "partially_indexed"
FAILED_DIR          = "failed"

# Ensure directories exist
for d in (FULLY_INDEXED_DIR, PARTIAL_INDEXED_DIR, FAILED_DIR):
    os.makedirs(d, exist_ok=True)

# === OCR Tools Paths ===
POPPLER_PATH  = r"D:\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

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

def parse_fields(text):
    # Define all possible labels for name and account number
    import logging
    name_labels = [
        r"Name of Account Holder(?:\s*\(corporate entities\))?",
        r"First names?", r"First name", r"Surname(?:\s*\(individual\))?", r"Surnames", r"Account Name", r"Institution Name"
    ]
    account_labels = [
        r"UMB-IHL ID Number", r"ID number", r"CSD Number", r"Client CSD Securities Account No", r"Account Number", r"Account number", r"Account no", r"Account no\."
    ]

    def make_patterns(labels, val_pattern):
        # Allow for extra/missing spaces, optional parentheses, colon/dash, and case-insensitive
        return [re.compile(rf"{label}\s*[:\-]?\s*({val_pattern})?", re.IGNORECASE) for label in labels]

    name_patterns = make_patterns(name_labels, r"[A-Za-z ,.'-]+")
    account_patterns = make_patterns(account_labels, r"[A-Za-z0-9\-]+")

    lines = text.splitlines()
    name = None
    account = None
    # Blacklist all label-like and generic words, including all label variants
    blacklist = {"Branch", "Account", "Name", "Surname", "Other", "Print", "Institution", "Other name", "Other names", "Print name", "Account Name", "Name of Account Holder", "First name", "First names", "Surnames", "Institution Name"}
    def is_valid(val):
        # Only accept values that are not in the blacklist and not just label text
        return val and val.strip() not in blacklist and len(val.strip()) > 2

    # Helper to log matches
    def log_match(label, line, value):
        print(f"[OCR DEBUG] Matched label '{label}' in line: '{line}' -> Value: '{value}'")

    # Search for name (same line, then next line if not found)
    for i, line in enumerate(lines):
        for pat, label in zip(name_patterns, name_labels):
            m = pat.search(line)
            if m:
                candidate = m.group(1)
                if candidate and is_valid(candidate.strip()):
                    candidate = candidate.strip().replace(" ", "_")
                    log_match(label, line, candidate)
                    name = candidate
                    break
                # If no value on same line, check next line
                elif i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    # Only consider next line if it looks like a name (letters, not blacklisted)
                    if is_valid(next_line) and re.match(r"^[A-Za-z ,.'-]+$", next_line):
                        candidate = next_line.replace(" ", "_")
                        log_match(label + " (next line)", lines[i+1], candidate)
                        name = candidate
                        break
        if name:
            break

    # Search for account number (same line, then next line if not found)
    for i, line in enumerate(lines):
        for pat, label in zip(account_patterns, account_labels):
            m = pat.search(line)
            if m:
                candidate = m.group(1)
                if candidate and is_valid(candidate.strip()):
                    candidate = candidate.strip()
                    log_match(label, line, candidate)
                    account = candidate
                    break
                elif i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if is_valid(next_line) and re.match(r"^[A-Za-z0-9\-]+$", next_line):
                        candidate = next_line
                        log_match(label + " (next line)", lines[i+1], candidate)
                        account = candidate
                        break
        if account:
            break

    return name, account

# === Routing Logic ===
def route_file(src_path):
    filename = os.path.basename(src_path)
    ext = os.path.splitext(filename)[1].lower()
    text = extract_text(src_path)
    name, account = parse_fields(text)
    is_image = ext in [".png", ".jpg", ".jpeg"]

    if name and account:
        new_filename = f"{name}_{account}.pdf" if is_image else f"{name}_{account}{ext}"
        dest_dir = FULLY_INDEXED_DIR
    elif name or account:
        key = name or account
        new_filename = f"{key}.pdf" if is_image else f"{key}{ext}"
        dest_dir = PARTIAL_INDEXED_DIR
    else:
        new_filename = filename
        dest_dir = FAILED_DIR

    dest_path = os.path.join(dest_dir, new_filename)
    base, extn = os.path.splitext(new_filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_dir, f"{base}_{counter}{extn}")
        counter += 1

    if dest_dir == FAILED_DIR:
        if safe_move_file(src_path, dest_path):
            print(f"[{dest_dir.upper()}] {filename} → {new_filename}")
        return

    if is_image:
        try:
            img = Image.open(src_path).convert("RGB")
            img.save(dest_path, "PDF", resolution=100.0)
            if os.path.exists(src_path):
                os.remove(src_path)
            print(f"[{dest_dir.upper()}] {filename} → {new_filename} (converted to PDF)")
        except Exception as e:
            print(f"[ERROR] Failed to convert {filename} to PDF: {e}")
            if os.path.exists(src_path):
                fallback = os.path.join(FAILED_DIR, filename)
                safe_move_file(src_path, fallback)
                print(f"[FAILED] {filename} → {filename}")
    else:
        if safe_move_file(src_path, dest_path):
            print(f"[{dest_dir.upper()}] {filename} → {new_filename}")

# === Watcher Handler ===
class ScanHandler(FileSystemEventHandler):
    _lock = threading.Lock()
    _timer = None

    def _delayed_batch_process(self):
        with self._lock:
            ScanHandler._timer = None
        time.sleep(5)
        files = [f for f in os.listdir(SCAN_DIR) if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))]
        for fname in files:
            fpath = os.path.join(SCAN_DIR, fname)
            if not os.path.isfile(fpath):
                continue
            for attempt in range(10):
                try:
                    if not os.path.isfile(fpath):
                        break
                    with open(fpath, 'rb') as f:
                        f.read(1)
                    route_file(fpath)
                    break
                except Exception as e:
                    time.sleep(0.5)
            else:
                print(f"[ERROR] Failed to process {fpath} after multiple attempts.")

    def _schedule_batch(self):
        with self._lock:
            if ScanHandler._timer is not None:
                ScanHandler._timer.cancel()
            ScanHandler._timer = threading.Timer(0.5, self._delayed_batch_process)
            ScanHandler._timer.start()

    def on_created(self, event):
        if not event.is_directory:
            self._schedule_batch()

    def on_moved(self, event):
        if not event.is_directory:
            self._schedule_batch()

def start_watcher():
    abs_path = os.path.abspath(SCAN_DIR)
    print(f"[WATCHING] {abs_path} → (fully|partial|failed)")
    os.makedirs(SCAN_DIR, exist_ok=True)
    obs = Observer()
    obs.schedule(ScanHandler(), path=SCAN_DIR, recursive=False)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

from fastapi import FastAPI, Query
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


def main():
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

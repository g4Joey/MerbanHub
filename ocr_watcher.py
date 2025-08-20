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

# === Retry-safe file move ===
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
    if dest_dir == FAILED_DIR:
        if safe_move_file(src_path, dest_path):
            logging.info(f"[{dest_dir.upper()}] {filename} → {new_filename}")
        return
    if is_image:
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

# === Watcher Handler ===
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

@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()


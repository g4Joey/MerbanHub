import os
import time
import shutil
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === Directories ===
SCAN_DIR            = "incoming-scan"
FULLY_INDEXED_DIR   = "fully_indexed"
PARTIAL_INDEXED_DIR = "partially_indexed"
FAILED_DIR          = "failed"

# Make sure these exist
for d in (FULLY_INDEXED_DIR, PARTIAL_INDEXED_DIR, FAILED_DIR):
    os.makedirs(d, exist_ok=True)

# === OCR Tools ===
POPPLER_PATH  = r"D:\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"  # adjust as needed
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"               # adjust as needed
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# === Helpers ===

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        try:
            pages = convert_from_path(path, poppler_path=POPPLER_PATH)
        except Exception as e:
            print(f"[ERROR] PDF conversion failed: {e}")
            return ""
        text = "".join(pytesseract.image_to_string(p) for p in pages)
    else:
        img = Image.open(path).convert("RGB")
        text = pytesseract.image_to_string(img)
    return text

def parse_fields(text):
    m_name    = re.search(r"name\s*:\s*([A-Za-z ]+)", text, re.IGNORECASE)
    m_account = re.search(r"account\s*no\s*[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    name    = m_name.group(1).strip().replace(" ", "_") if m_name else None
    account = m_account.group(1).strip()                if m_account else None
    return name, account

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
        new_filename = filename  # keep original
        dest_dir = FAILED_DIR

    dest_path = os.path.join(dest_dir, new_filename)

    if dest_dir == FAILED_DIR:
        # Just move the file as-is
        shutil.move(src_path, dest_path)
        print(f"[{dest_dir.upper()}] {filename} → {new_filename}")
        return

    if is_image:
        # Convert image to PDF and save as new file, then remove original
        if not os.path.exists(src_path):
            print(f"[SKIP] Source image missing before conversion: {src_path}")
            return
        try:
            img = Image.open(src_path).convert("RGB")
            img.save(dest_path, "PDF", resolution=100.0)
            if os.path.exists(src_path):
                os.remove(src_path)
            print(f"[{dest_dir.upper()}] {filename} → {new_filename} (converted to PDF)")
        except Exception as e:
            print(f"[ERROR] Failed to convert {filename} to PDF: {e}")
            # If conversion fails, move to failed as original (if it still exists)
            if os.path.exists(src_path):
                fail_path = os.path.join(FAILED_DIR, filename)
                shutil.move(src_path, fail_path)
                print(f"[FAILED] {filename} → {filename}")
            else:
                print(f"[SKIP] Source image missing after failed conversion: {src_path}")
    else:
        shutil.move(src_path, dest_path)
        print(f"[{dest_dir.upper()}] {filename} → {new_filename}")

# === Watcher ===


class ScanHandler(FileSystemEventHandler):
    def _process(self, path):
        if not path.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
            return
        # Add a small initial delay to give the OS time to finish file operations
        time.sleep(0.3)
        last_exception = None
        for attempt in range(10):
            try:
                if not os.path.isfile(path):
                    raise FileNotFoundError(f"{path} not found (attempt {attempt+1})")
                with open(path, 'rb') as f:
                    f.read(1)
                route_file(path)
                return
            except Exception as e:
                last_exception = e
                time.sleep(0.5)
        print(f"[ERROR] Failed to process {path} after multiple attempts: {last_exception}")

    def on_created(self, event):
        if event.is_directory:
            return
        self._process(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._process(event.dest_path)

    def on_modified(self, event):
        # Optionally process modified files (uncomment if needed)
        # if event.is_directory:
        #     return
        # self._process(event.src_path)
        pass

def start_watcher():
    abs_scan_dir = os.path.abspath(SCAN_DIR)
    print(f"[WATCHING] {abs_scan_dir} → (fully|partial|failed)")
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

if __name__ == "__main__":
    start_watcher()

import os
import time
import shutil
import pytesseract
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re

# Set paths
SCAN_DIR = "incoming-scan"
PROCESSED_DIR = "processed"

# If using Windows and tesseract is not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[ERROR] Failed to convert or OCR: {e}")
    return text

def parse_metadata(text):
    # Very basic regex — improve as needed
    name_match = re.search(r"Client[:\-]?\s*(\w+)\s+(\w+)", text)
    acc_match = re.search(r"ACC\d+", text)
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", text)

    first, last = name_match.groups() if name_match else ("Unknown", "Client")
    acc = acc_match.group() if acc_match else "ACC0000"
    date = date_match.group() if date_match else "0000-00-00"

    return f"{last}_{first}_{acc}_{date}.pdf"

def process_pdf(file_path):
    print(f"[INFO] Processing file: {file_path}")
    text = extract_text_from_pdf(file_path)
    new_filename = parse_metadata(text)
    new_path = os.path.join(PROCESSED_DIR, new_filename)

    try:
        shutil.move(file_path, new_path)
        print(f"[SUCCESS] Moved and renamed to: {new_path}")
    except Exception as e:
        print(f"[ERROR] Could not move file: {e}")

class ScanHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            time.sleep(1)  # wait for file to finish writing
            process_pdf(event.src_path)

def start_watcher():
    print("[WATCHING] Folder:", SCAN_DIR)
    observer = Observer()
    observer.schedule(ScanHandler(), path=SCAN_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    os.makedirs(SCAN_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    start_watcher()

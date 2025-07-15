import os
import time
import shutil
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === Paths ===
SCAN_DIR = "incoming-scan"
PROCESSED_DIR = "processed"

# External tools
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"
TESSERACT_CMD = r"C:\Users\KC-USER\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# === Core functions ===

def convert_image_to_pdf(image_path):
    img = Image.open(image_path).convert("RGB")
    pdf_filename = os.path.splitext(os.path.basename(image_path))[0] + ".pdf"
    pdf_path = os.path.join(PROCESSED_DIR, pdf_filename)
    img.save(pdf_path)
    print(f"[INFO] Converted image to PDF: {pdf_path}")
    return pdf_path

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        for img in images:
            text += pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[ERROR] Failed to convert or OCR: {e}")
    return text

def parse_metadata(text):
    name_match = re.search(r"Client[:\-]?\s*(\w+)\s+(\w+)", text)
    acc_match = re.search(r"ACC\d+", text)
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", text)

    first, last = name_match.groups() if name_match else ("Unknown", "Client")
    acc = acc_match.group() if acc_match else "ACC0000"
    date = date_match.group() if date_match else "0000-00-00"

    return f"{last}_{first}_{acc}_{date}.pdf"

def process_file(file_path):
    print(f"[INFO] Processing file: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".png", ".jpg", ".jpeg"]:
        # If it's an image → convert to PDF in processed/
        pdf_path = convert_image_to_pdf(file_path)
        # Delete the original image to keep things tidy
        os.remove(file_path)
        file_path = pdf_path

    text = extract_text_from_pdf(file_path)
    new_filename = parse_metadata(text)
    new_path = os.path.join(PROCESSED_DIR, new_filename)

    # If the file is already in PROCESSED_DIR, just rename it
    if os.path.dirname(file_path) == os.path.abspath(PROCESSED_DIR):
        os.rename(file_path, new_path)
    else:
        shutil.move(file_path, new_path)

    print(f"[SUCCESS] Saved to: {new_path}")

# === Watchdog ===

class ScanHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
            time.sleep(1)
            process_file(event.src_path)

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

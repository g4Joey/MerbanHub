def correct_common_ocr_errors(value):
    # Only apply context-specific corrections if needed (not global)
    # This function is now a placeholder for future context-aware corrections
    return value

def validate_and_correct_surname(surname):
    # Only correct known OCR errors, do not restrict to a set
    if surname == "Otog":
        return "Otoo"
    # Add more context-specific corrections as needed
    return surname
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
import requests

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
POPPLER_PATH  = r"D:\\Downloads\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin"
TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# === OCR & Parsing ===
def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    print(f"[DEBUG] Starting extract_text for {path}")
    logging.debug(f"Starting extract_text for {path}")
    try:
        if ext == ".pdf":
            # Lower DPI for troubleshooting
            pages = convert_from_path(path, poppler_path=POPPLER_PATH, dpi=300)
            print(f"[DEBUG] PDF has {len(pages)} pages")
            logging.debug(f"PDF has {len(pages)} pages")
            texts = []
            for idx, p in enumerate(pages):
                try:
                    img_path = os.path.join(DEBUG_DIR, f"{os.path.splitext(os.path.basename(path))[0]}_page{idx+1}.png")
                    p.save(img_path)
                    print(f"[DEBUG] Saved page {idx+1} as {img_path}")
                    logging.debug(f"Saved page {idx+1} as {img_path}")
                    print(f"[DEBUG] OCR on page {idx+1} of {len(pages)}")
                    logging.debug(f"OCR on page {idx+1} of {len(pages)}")
                    t = pytesseract.image_to_string(p)
                    texts.append(t)
                except Exception as page_e:
                    msg = f"[ERROR] OCR failed on page {idx+1}: {page_e}"
                    print(msg)
                    logging.error(msg)
            text = "\n".join(texts)
        else:
            img = Image.open(path).convert("RGB")
            text = pytesseract.image_to_string(img)
        print(f"[DEBUG] Finished extract_text for {path}, length: {len(text)}")
        logging.debug(f"Finished extract_text for {path}, length: {len(text)}")
        return text
    except Exception as e:
        msg = f"Text extraction failed for {path}: {e}"
        print(msg)
        logging.error(msg)
        return ""

def normalize(val):
    # Lowercase, remove underscores, spaces, punctuation
    return re.sub(r'[^a-z0-9]', '', val.lower())

def sanitize_filename(name):
    """Sanitize and truncate filename to be filesystem-safe"""
    if not name:
        return "Unknown"
    
    # Remove invalid filename characters
    safe_name = re.sub(r'[\\/:*?"<>|]', ' ', name).replace('_', ' ').strip()
    safe_name = re.sub(r'\s+', ' ', safe_name)
    
    # Truncate to reasonable length (max 100 chars)
    if len(safe_name) > 100:
        safe_name = safe_name[:100].strip()
    
    # Validate/correct surname if possible (only known OCR errors)
    name_parts = safe_name.split()
    if len(name_parts) > 1:
        name_parts[-1] = validate_and_correct_surname(name_parts[-1])
        safe_name = ' '.join(name_parts)
    
    # If it's still too long or contains problematic patterns, use fallback
    if len(safe_name) > 50 or any(word in safe_name.lower() for word in ['investment', 'objectives', 'planning', 'primary source', 'retirement']):
        # Extract only the first few meaningful words
        words = safe_name.split()[:3]
        safe_name = ' '.join(words)
    
    # Final fallback
    if not safe_name or len(safe_name) < 2:
        return "Unknown"
    
    return safe_name

def parse_fields(text, img_path=None):
    # All possible labels (case-insensitive, with/without colon, underscore, etc.)
    labels = [
        "Name of Account Holder", "First name", "First names", "Surname", "Surnames",
        "Other name", "Other names", "Print name", "Account Name", "Institution Name",
        "Account Number", "Account number", "Account no", "CSD Number", "CSD NO", "Client CSD Securities Account No",
        "ID number", "UMB-IHL ID Number", "Name", "Name of Organisation", "Name of Organization"
    ]
    label_norms = set([normalize(l) for l in labels])
    # Build regex for label matching (with/without colon, case-insensitive)
    label_regex = re.compile(rf"({'|'.join([re.escape(l) for l in labels])})\s*:?", re.IGNORECASE)

    # Strong blacklist: all label variants, generic words, and normalized forms
    blacklist = set(label_norms)
    blacklist.update([normalize(x) for x in [
        "Branch", "Account", "Name", "Surname", "Other", "Print", "Institution", "Organization", "Organisation", "No", "Number", "Holder", "CSD", "ID", "Client", "Details", "Purpose", "Period", "Address", "Tel", "E-Mail", "PHOTO", "Reference", "Date", "Relationship", "Employer", "Spouse", "Failed", "Partial", "Indexed", "Fully", "Of", "The", "And", "Or", "As", "It", "Is", "Are", "Was", "Be", "On", "In", "At", "To", "For", "By", "With", "From", "This", "That", "These", "Those", "A", "An", "PDF", "JPG", "PNG", "Doc", "File", "Scan", "Image", "Document", "Page", "Test", "Sample", "Unknown", "Unnamed", "Blank", "Empty", "None", "Null", "Untitled", 
        # Add OCR-specific problematic patterns
        "Investment", "Objectives", "Planning", "Retirement", "Education", "Mortgage", "Income", "Others", "Horizon", "Short", "Term", "Medium", "Long", "Year", "Years", "Below", "Above", "Annual", "Under", "Over", "Knowledge", "Sophisticated", "Good", "Fair", "Novice", "Risk", "Tolerance", "Low", "High", "Amount", "Treasury", "Bills", "Mutual", "Funds", "Bonds", "Stocks", "Insurance", "Government", "Day", "Govt", "Notes", "Instructions", "Disposal", "Invest", "Reinvest", "Principal", "Maturity", "Proceeds", "Bank", "Mobile", "Money", "Transfer", "Hold", "Any", "Declare", "Information", "Evaluate", "Financial", "Needs", "Merchant", "Group", "Undertake", "Notify", "Promptly", "Signature", "Signing", "Remarks", "Manager", "AML", "Info", "PEP", "Undesirable", "Watchlist", "Blacklist", "Electoral", "Polling", "Station", "Code", "Voter", "Registration", "Search", "WhatsApp", "https", "www", "com", "Valid", "Passport", "Male", "Female", "Gender", "Telephone", "Postal", "Residential", "Nationality", "Country", "Marital", "Status", "Married", "Single", "Widowed", "Divorced", "Occupation", "Primary", "Source", "Title", "Mr", "Mrs", "Miss", "Ms", "Dr", "Prof"
    ]])

    # Add patterns to detect problematic extractions
    def is_valid_name_extraction(text):
        if not text or len(text) < 2:
            return False
        # Reject if too long (likely form text)
        if len(text) > 100:
            return False
        # Reject if contains too many brackets or special chars
        if text.count('[') > 2 or text.count(']') > 2 or text.count('(') > 2:
            return False
        # Reject if contains URLs or email patterns
        if 'http' in text.lower() or '@' in text or '.com' in text.lower():
            return False
        # Reject if contains too many numbers relative to letters
        letters = sum(c.isalpha() for c in text)
        numbers = sum(c.isdigit() for c in text)
        if numbers > letters and letters < 3:
            return False
        return True

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
    # Collect possible name parts by label
    name_parts = {}
    name_labels = [
        "First name", "First names", "Other name", "Other names", "Surname", "Surnames", "Account Name", "Name of Account Holder", "Name", "Name of Organisation", "Name of Organization"
    ]
    for idx, line in enumerate(lines):
        extracted_boxes = []  # Ensure this is defined for each label extraction
        match = label_regex.search(line)
        if match:
            label = match.group(1)
            after_label = line[match.end():].strip()
            value_words = []
            # 1. Collect words after label on the same line
            for word in after_label.split():
                nword = normalize(word)
                if nword in label_norms or nword in blacklist:
                    break
                value_words.append(word)
            # 2. If not found, check subsequent lines up to next non-name/account label
            if not value_words:
                next_idx = idx + 1
                while next_idx < len(lines):
                    next_line = lines[next_idx].strip()
                    # If next line is empty, skip
                    if not next_line:
                        next_idx += 1
                        continue
                    # If next line starts with a label that is NOT a name or account number, stop
                    next_match = label_regex.match(next_line)
                    if next_match:
                        next_label = next_match.group(1)
                        # Only continue if next label is a name or account number label
                        if next_label not in name_labels and next_label not in [
                            "Account Number", "Account number", "Account no", "CSD Number", "Client CSD Securities Account No", "ID number", "UMB-IHL ID Number"
                        ]:
                            break
                        # Otherwise, skip the label and continue
                        after_next_label = next_line[next_match.end():].strip()
                        for word in after_next_label.split():
                            nword = normalize(word)
                            if nword in label_norms or nword in blacklist:
                                break
                            value_words.append(word)
                    else:
                        # Not a label, just collect words
                        for word in next_line.split():
                            nword = normalize(word)
                            if nword in label_norms or nword in blacklist:
                                break
                            value_words.append(word)
                    next_idx += 1
            value = " ".join(value_words).strip()
            if ocr_data is not None and value:
                value_set = set([normalize(w) for w in value.split()])
                for i, w in enumerate(ocr_data["text"]):
                    if normalize(w) in value_set and int(ocr_data["conf"][i]) > 50:
                        x, y, w_, h_ = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                        extracted_boxes.append((x, y, w_, h_, label, w))
                # ...existing blue/ink logic...
                for i, w in enumerate(ocr_data["text"]):
                    if normalize(w) == normalize(value):
                        conf = ocr_data["conf"][i]
                        logging.debug(f"OCR confidence for '{w}': {conf}")
                        if int(conf) <= 50:
                            continue
                        x, y, w_, h_ = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                        roi = color_data[y:y+h_, x:x+w_]
                        avg_color = np.mean(roi, axis=(0, 1))
                        if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:
                            logging.debug(f"Matched label '{label}' (blue/ink) in line: '{line}' -> Value: '{value}'")
                            break
                else:
                    logging.debug(f"Matched label '{label}' in line: '{line}' -> Value: '{value}' (not blue/ink)")
            else:
                logging.debug(f"Matched label '{label}' in line: '{line}' -> Value: '{value}'")

            # Only process if label is a name label
            if label in name_labels:
                # First check if extraction looks valid
                if not is_valid_name_extraction(value):
                    logging.debug(f"Name extraction '{value}' from label '{label}' rejected: invalid pattern.")
                    continue
                    
                # Each part must have at least one word with 2+ consecutive letters
                def has_valid_word(val):
                    return any(re.match(r"[A-Za-z]{2,}", w) for w in val.split())
                if value and has_valid_word(value):
                    name_parts[label] = value
                else:
                    logging.debug(f"Name part '{value}' from label '{label}' rejected: no word with 2+ consecutive letters.")

    # Assemble all valid name parts in order: First, Other, Surname
    ordered_labels = ["First name", "First names", "Other name", "Other names", "Surname", "Surnames"]
    valid_parts = []
    for l in ordered_labels:
        if l in name_parts and any(re.match(r"[A-Za-z]{2,}", w) for w in name_parts[l].split()):
            valid_parts.append(name_parts[l])
    if valid_parts:
        full_name = " ".join(valid_parts)
        return full_name, "+".join([l for l in ordered_labels if l in name_parts])
    # Otherwise, try single name label (Account Name, Name of Account Holder, etc.)
    for l in ["Account Name", "Name of Account Holder", "Name", "Name of Organisation", "Name of Organization"]:
        if l in name_parts:
            candidate_name = name_parts[l]
            # Additional validation for single name labels
            if not is_valid_name_extraction(candidate_name):
                logging.debug(f"Name '{candidate_name}' from label '{l}' rejected: invalid pattern.")
                continue
            # Reject if name starts with (s) (case-insensitive, allow optional spaces)
            if re.match(r"^\(s\)\s*", candidate_name, re.IGNORECASE):
                logging.debug(f"Name '{candidate_name}' from label '{l}' rejected: starts with (s)."); continue
            # Reject if name is exactly 'Joint' (case-insensitive, allow leading/trailing spaces)
            if candidate_name.strip().lower() == "joint":
                logging.debug(f"Name '{candidate_name}' from label '{l}' rejected: name is exactly 'Joint'."); continue
            # Must have at least one word with 2+ consecutive letters
            words = candidate_name.split()
            if any(re.match(r"[A-Za-z]{2,}", w) for w in words):
                # Reject if all words are single letters or numbers (e.g. 'G Y Q _25', 'A Z U')
                if not all(len(w) == 1 or not re.match(r"[A-Za-z]{2,}", w) for w in words):
                    # Always join with a single space to normalize spacing
                    normalized_name = ' '.join(words)
                    return normalized_name, l
                else:
                    logging.debug(f"Name '{candidate_name}' from label '{l}' rejected: all words are single letters or invalid.")
            else:
                logging.debug(f"Name '{candidate_name}' from label '{l}' rejected: no word with 2+ consecutive letters.")
    # If nothing valid found, check for standalone 'Commission' and reject only if it's the only candidate
    if 'commission' in [normalize(v) for v in name_parts.values()] and len(name_parts) == 1:
        logging.debug("Only 'Commission' found as name, rejecting as too generic.")
        return None, None
    logging.debug("No valid value found for any label. Failing job.")
    return None, None

def is_valid_account(val):
    # Only accept if at least 10 digits, and mostly 13 digits
    digits = ''.join([c for c in val if c.isdigit()])
    return len(digits) >= 10 and (len(digits) == 13 or len(digits) >= 10)

# === Routing Logic ===
def route_file(src_path):
    filename = os.path.basename(src_path)
    ext = os.path.splitext(filename)[1].lower()
    print(f"[DEBUG] route_file: extracting text from {src_path}")
    logging.debug(f"route_file: extracting text from {src_path}")
    text = extract_text(src_path)
    print(f"[DEBUG] route_file: parse_fields on extracted text (length {len(text)})")
    logging.debug(f"route_file: parse_fields on extracted text (length {len(text)})")
    ext = os.path.splitext(src_path)[1].lower()

    # --- Manual override for specific files ---
    manual_name_overrides = {
        "from_Leticia_Asamoah_Essah.pdf": "Leticia Asamoah Essah.pdf",
        "Dovene's_Aibert.pdf": "Albert Kobina Amonoo.pdf"
    }
    if filename in manual_name_overrides:
        name = manual_name_overrides[filename]
        name_label = "MANUAL_OVERRIDE"
        print(f"[DEBUG] Manual override: name={name}, name_label={name_label}")
        logging.debug(f"Manual override: name={name}, name_label={name_label}")
    else:
        if ext in [".png", ".jpg", ".jpeg"]:
            name, name_label = parse_fields(text, src_path)
        else:
            name, name_label = parse_fields(text, None)
        print(f"[DEBUG] parse_fields result: name={name}, name_label={name_label}")
        logging.debug(f"parse_fields result: name={name}, name_label={name_label}")
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
        print(f"[DEBUG] Moving {filename} to FAILED_DIR")
        dest_path = os.path.join(FAILED_DIR, filename)
        safe_move_file(src_path, dest_path)
        return
    is_image = ext in [".png", ".jpg", ".jpeg"]
    if name and account:
        # Sanitize and truncate name for filename safety
        safe_name = sanitize_filename(name)
        safe_account = re.sub(r'[\\/:*?"<>|]', '', account)
        new_filename = f"{safe_name} {safe_account}.pdf" if is_image else f"{safe_name} {safe_account}{ext}"
        dest_dir = FULLY_INDEXED_DIR
        status = "FULLY_INDEXED"
        print(f"[DEBUG] Moving {filename} to FULLY_INDEXED as {new_filename}")
    elif name or account:
        key = name or account
        safe_key = sanitize_filename(key)
        new_filename = f"{safe_key}.pdf" if is_image else f"{safe_key}{ext}"
        dest_dir = PARTIAL_INDEXED_DIR
        status = "PARTIAL_INDEXED"
        print(f"[DEBUG] Moving {filename} to PARTIAL_INDEXED as {new_filename}")
    else:
        # This should not be reached, but fallback to failed
        new_filename = filename
        dest_dir = FAILED_DIR
        status = "FAILED"
        print(f"[DEBUG] Moving {filename} to FAILED_DIR (should not reach here)")
    dest_path = os.path.join(dest_dir, new_filename)
    base, extn = os.path.splitext(new_filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_dir, f"{base}_{counter}{extn}")
        counter += 1
    
    # Additional safety check for filename length and validity
    if len(os.path.basename(dest_path)) > 255:
        # Use a safe fallback filename
        timestamp = str(int(time.time()))
        safe_filename = f"Document_{timestamp}{ext}"
        dest_path = os.path.join(dest_dir, safe_filename)
        logging.warning(f"Filename too long, using fallback: {safe_filename}")
    
    if dest_dir == FAILED_DIR:
        if safe_move_file(src_path, dest_path):
            logging.info(f"[{dest_dir.upper()}] {filename} → {os.path.basename(dest_path)}")
        return
    if is_image:
        try:
            img = Image.open(src_path).convert("RGB")
            img.save(dest_path, "PDF", resolution=100.0)
            if os.path.exists(src_path):
                os.remove(src_path)
            logging.info(f"[{dest_dir.upper()}] {filename} → {os.path.basename(dest_path)} (converted to PDF)")
        except Exception as e:
            logging.error(f"Failed to convert {filename} to PDF: {e}")
            # Move to FAILED_DIR if conversion fails
            timestamp = str(int(time.time()))
            fallback_name = f"Failed_{timestamp}{os.path.splitext(filename)[1]}"
            fallback_path = os.path.join(FAILED_DIR, fallback_name)
            if safe_move_file(src_path, fallback_path):
                logging.info(f"[FAILED] {filename} → {fallback_name}")
    else:
        # Try to move the file, with fallback on failure
        if not safe_move_file(src_path, dest_path):
            # If move failed (likely due to filename issues), use fallback
            timestamp = str(int(time.time()))
            fallback_name = f"Failed_{timestamp}{ext}"
            fallback_path = os.path.join(FAILED_DIR, fallback_name)
            if safe_move_file(src_path, fallback_path):
                logging.info(f"[FAILED] {filename} → {fallback_name} (filename issue)")
                dest_path = fallback_path  # Update for integration calls
            else:
                logging.error(f"Failed to move {filename} even to fallback location")
                return
        else:
            logging.info(f"[{dest_dir.upper()}] {filename} → {os.path.basename(dest_path)}")

    # --- Integration: Upload file and metadata to Java backend ---
    try:
        # Upload file
        files = {'file': open(dest_path, 'rb')}
        upload_resp = requests.post('http://localhost:8080/api/files/upload', files=files, timeout=10)
        logging.info(f"[INTEGRATION] Uploaded file to Java backend: {upload_resp.text}")
    except Exception as e:
        logging.error(f"[INTEGRATION] File upload failed: {e}")

    try:
        # Send metadata
        meta = {
            "originalFileName": filename,
            "newFileName": new_filename,
            "clientName": name or "",
            "accountNumber": account or "",
            "status": status
        }
        meta_resp = requests.post('http://localhost:8080/api/ocr/notify', json=meta, timeout=10)
        logging.info(f"[INTEGRATION] Sent metadata to Java backend: {meta_resp.text}")
    except Exception as e:
        logging.error(f"[INTEGRATION] Metadata notify failed: {e}")

# === Watcher Handler ===
class ScanHandler(FileSystemEventHandler):
    _lock = threading.Lock()
    _timer = None

    def _delayed_batch_process(self):
        with self._lock:
            ScanHandler._timer = None
        time.sleep(5)
        files = [f for f in os.listdir(SCAN_DIR) if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))]
        if not files:
            print(f"[DEBUG] No supported files found in {SCAN_DIR} at this batch.")
            logging.debug(f"No supported files found in {SCAN_DIR} at this batch.")
        else:
            print(f"[DEBUG] Found files in {SCAN_DIR}: {files}")
            logging.debug(f"Found files in {SCAN_DIR}: {files}")
        for fname in files:
            fpath = os.path.join(SCAN_DIR, fname)
            print(f"[DEBUG] About to process file: {fpath}")
            logging.debug(f"About to process file: {fpath}")
            if not os.path.isfile(fpath):
                print(f"[DEBUG] Skipping non-file: {fpath}")
                logging.debug(f"Skipping non-file: {fpath}")
                continue
            try:
                with open(fpath, 'rb') as f:
                    f.read(1)
                print(f"[DEBUG] Processing file: {fpath}")
                logging.debug(f"Processing file: {fpath}")
                route_file(fpath)
            except Exception as e:
                print(f"[DEBUG] Exception while processing {fpath}: {e}")
                logging.debug(f"Exception while processing {fpath}: {e}")
                # Move to FAILED_DIR immediately if processing fails
                dest_path = os.path.join(FAILED_DIR, os.path.basename(fpath))
                safe_move_file(fpath, dest_path)
                logging.error(f"Moved {fpath} to {dest_path} due to processing error.")

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
    msg = f"[WATCHING] {abs_path} → (fully|partial|failed)"
    print(msg)
    logging.info(msg)
    os.makedirs(SCAN_DIR, exist_ok=True)

    # Process all files in SCAN_DIR on startup
    startup_files = [f for f in os.listdir(SCAN_DIR) if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))]
    if startup_files:
        print(f"[DEBUG] Startup: Found files in {SCAN_DIR}: {startup_files}")
        logging.debug(f"Startup: Found files in {SCAN_DIR}: {startup_files}")
    for fname in startup_files:
        fpath = os.path.join(SCAN_DIR, fname)
        print(f"[DEBUG] Startup: About to process file: {fpath}")
        logging.debug(f"Startup: About to process file: {fpath}")
        if not os.path.isfile(fpath):
            print(f"[DEBUG] Startup: Skipping non-file: {fpath}")
            logging.debug(f"Startup: Skipping non-file: {fpath}")
            continue
        try:
            with open(fpath, 'rb') as f:
                f.read(1)
            print(f"[DEBUG] Startup: Processing file: {fpath}")
            logging.debug(f"Startup: Processing file: {fpath}")
            route_file(fpath)
        except Exception as e:
            print(f"[DEBUG] Startup: Exception while processing {fpath}: {e}")
            logging.debug(f"Startup: Exception while processing {fpath}: {e}")
            # Move to FAILED_DIR immediately if processing fails
            dest_path = os.path.join(FAILED_DIR, os.path.basename(fpath))
            safe_move_file(fpath, dest_path)
            logging.error(f"Startup: Moved {fpath} to {dest_path} due to processing error.")

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

import subprocess

def check_poppler():
    try:
        pdftoppm_path = os.path.join(POPPLER_PATH, 'pdftoppm.exe')
        result = subprocess.run([pdftoppm_path, '-h'], capture_output=True, text=True)
        if result.returncode != 0:
            print('[ERROR] Poppler (pdftoppm.exe) not working or not found in the specified path!')
            print(result.stderr)
            logging.error('Poppler (pdftoppm.exe) not working or not found in the specified path!')
            return False
        print('[OK] Poppler found and working.')
        return True
    except Exception as e:
        print(f'[ERROR] Exception while checking Poppler: {e}')
        logging.error(f'Exception while checking Poppler: {e}')
        return False

def main():
    # Add console handler to logging so all logs also print to terminal
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    if not check_poppler():
        print('[FATAL] Poppler is not available. Exiting.')
        return
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()


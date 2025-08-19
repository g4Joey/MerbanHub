import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re

pdf_path = "sample.pdf"
poppler_path = r"C:\\poppler-24.08.0\\Library\\bin"
os.makedirs("test_images", exist_ok=True)
os.makedirs("review", exist_ok=True)

client_labels = [
    "Name of Account Holder", "First name", "First names", "Surname", "Surnames",
    "Other name", "Other names", "Print name", "Account Name", "Institution Name",
    "Account Number", "Account number", "Account no", "CSD Number", "Client CSD Securities Account No",
    "ID number", "UMB-IHL ID Number", "Name", "Name of Organisation", "Name of Organization"
]
client_labels = [lbl.lower() for lbl in client_labels]
label_norms = set([re.sub(r'[^a-z0-9]', '', l) for l in client_labels])

CONFIDENCE_THRESHOLD = 75  # Adjusted for experimentation

def normalize(val):
    return re.sub(r'[^a-z0-9]', '', val.lower())

def preprocess_for_ocr(pil_img):
    rgb = np.array(pil_img)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))  # Reduced clipLimit for finer contrast
    enhanced = clahe.apply(gray)
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)  # Adjusted parameters for smoother denoising
    binarized = cv2.adaptiveThreshold(denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3)  # Adjusted block size and constant
    return binarized

def extract_values(ocr_data):
    found_fields = set()
    field_confidences = []
    for j, word in enumerate(ocr_data["text"]):
        word_clean = word.strip().lower().rstrip(":")
        nword = normalize(word_clean)
        for label in client_labels:
            nlabel = normalize(label)
            if nword == nlabel or nword == normalize(label + ":"):
                # Try to get the next word(s) as the value (if it exists and is not a label)
                value_words = []
                k = j + 1
                while k < len(ocr_data["text"]):
                    next_word = ocr_data["text"][k].strip()
                    nnext = normalize(next_word)
                    if not next_word or nnext in label_norms:
                        break
                    value_words.append(next_word)
                    k += 1
                value = " ".join(value_words).strip()
                if value:
                    found_fields.add(normalize(value))
                    # Use the lowest confidence among value words as the field confidence
                    if value_words:
                        confs = [int(ocr_data['conf'][idx]) for idx in range(j+1, k) if ocr_data['conf'][idx] != '-1']
                        avg_conf = int(np.mean(confs)) if confs else 0
                    else:
                        avg_conf = 0
                    field_confidences.append((value, avg_conf))
                    print(f"[OCR DEBUG] Matched label '{label}' -> Value: '{value}' (avg confidence: {avg_conf})")
                break
    return found_fields, field_confidences

def highlight_fields(img_path, field_candidates, ocr_data):
    img = Image.open(img_path)
    arr = np.array(img)
    if len(arr.shape) == 2:
        arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    matches = []
    for i, w in enumerate(ocr_data["text"]):
        if w.strip() and normalize(w) in field_candidates:
            matches.append(i)
            print(f"[OCR DEBUG] Highlighted '{w}' with confidence {ocr_data['conf'][i]}")
    for i in matches:
        x, y = ocr_data["left"][i], ocr_data["top"][i]
        w_, h_ = ocr_data["width"][i], ocr_data["height"][i]
        cv2.rectangle(arr, (x, y), (x + w_, y + h_), (0, 255, 0), 2)
    debug_img_path = img_path.replace(".png", "_highlighted.png")
    cv2.imwrite(debug_img_path, arr)
    print(f"[DEBUG] Highlighted fields saved to {debug_img_path}")

try:
    pages = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=800)
    for i, page in enumerate(pages):
        img_path = f"test_images/page_{i + 1}.png"
        page.save(img_path, "PNG")
        binarized = preprocess_for_ocr(page)
        cv2.imwrite(img_path.replace('.png', '_binarized.png'), binarized)
        # Run both Tesseract engines
        ocr_data1 = pytesseract.image_to_data(binarized, output_type=pytesseract.Output.DICT, config="--oem 1")
        ocr_data0 = pytesseract.image_to_data(binarized, output_type=pytesseract.Output.DICT, config="--oem 0")
        found_fields1, confs1 = extract_values(ocr_data1)
        found_fields0, confs0 = extract_values(ocr_data0)
        # Choose the best engine for each field
        all_fields = {}
        for val, conf in confs1:
            if conf >= CONFIDENCE_THRESHOLD:
                all_fields[val] = conf
        for val, conf in confs0:
            if conf >= CONFIDENCE_THRESHOLD and (val not in all_fields or conf > all_fields[val]):
                all_fields[val] = conf
        if all_fields:
            highlight_fields(img_path, set(all_fields.keys()), ocr_data1)
        else:
            # Move to review if no field meets confidence threshold
            review_path = os.path.join("review", os.path.basename(img_path))
            os.rename(img_path, review_path)
            print(f"[REVIEW] No high-confidence fields found on page {i+1}. Moved to review queue.")
    print("[SUCCESS] PDF converted, preprocessed, OCRed, and fields highlighted or queued for review.")
except Exception as e:
    print("[ERROR] Something went wrong:", e)

import os
from pdf2image import convert_from_path


pdf_path = "sample.pdf"


poppler_path = r"C:\poppler-24.08.0\Library\bin"

os.makedirs("test_images", exist_ok=True)

try:
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    for i, img in enumerate(images):
        img.save(f"test_images/page_{i + 1}.png", "PNG")
    print("[SUCCESS] PDF converted to images successfully.")
except Exception as e:
    print("[ERROR] Something went wrong:", e)

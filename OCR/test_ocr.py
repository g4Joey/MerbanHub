import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("Using Tesseract at:", pytesseract.pytesseract.tesseract_cmd)
print("Does Tesseract file exist?:", os.path.exists(pytesseract.pytesseract.tesseract_cmd))
img = Image.open("test_images/page_1.png")

text = pytesseract.image_to_string(img)

print("\nExtracted text:\n")
print(text)

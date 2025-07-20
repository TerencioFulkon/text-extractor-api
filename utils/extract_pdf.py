import pdfplumber
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
            if text.strip():
                return text
    except Exception:
        pass  # fall through to OCR

    # Fallback to OCR
    try:
        images = convert_from_path(file_path)
        ocr_text = ""
        for image in images:
            ocr_text += pytesseract.image_to_string(image)
        return ocr_text
    except Exception as e:
        return f"[OCR failed: {str(e)}]"

from fastapi import FastAPI, UploadFile, File
import shutil
import os
import tempfile

from utils.extract_pdf import extract_text_from_pdf
from utils.extract_docx import extract_text_from_docx
from utils.extract_csv import extract_text_from_csv

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify exact origins later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Text Extractor API is running."}

# Replace or add this POST endpoint to receive the file correctly from Figma Make
@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        if suffix == ".pdf":
            text = extract_text_from_pdf(tmp_path)
            file_type = "pdf"
        elif suffix == ".docx":
            text = extract_text_from_docx(tmp_path)
            file_type = "docx"
        elif suffix == ".csv":
            text = extract_text_from_csv(tmp_path)
            file_type = "csv"
        else:
            text = "[Unsupported file type]"
            file_type = suffix

        return {
            "status": "success",
            "file_type": file_type,
            "text": text
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

from fastapi import FastAPI, UploadFile, File
import shutil
import os
import tempfile

from utils.extract_pdf import extract_text_from_pdf
from utils.extract_docx import extract_text_from_docx
from utils.extract_csv import extract_text_from_csv

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ceabd713-f5fb-4fc9-8801-90170d9dea0a-figmaiframepreview.figma.site"],  # Figma Make origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    try:
        suffix = os.path.splitext(file.filename)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Determine file type
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

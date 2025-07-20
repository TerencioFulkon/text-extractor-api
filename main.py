from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import tempfile
import os

from utils.extract_pdf import extract_text_from_pdf
from utils.extract_docx import extract_text_from_docx
from utils.extract_csv import extract_text_from_csv

app = FastAPI()

class ExtractRequest(BaseModel):
    file_url: str

@app.post("/extract-text")
def extract_text(req: ExtractRequest):
    try:
        response = requests.get(req.file_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="File could not be downloaded.")

        suffix = os.path.splitext(req.file_url)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(response.content)
            temp_path = temp.name

        if suffix == ".pdf":
            text = extract_text_from_pdf(temp_path)
        elif suffix == ".docx":
            text = extract_text_from_docx(temp_path)
        elif suffix == ".csv":
            text = extract_text_from_csv(temp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        return {
            "status": "success",
            "file_type": suffix.replace(".", ""),
            "text": text.strip()[:50000]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

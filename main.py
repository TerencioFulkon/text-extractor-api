from fastapi import FastAPI, UploadFile, File
import shutil
import os
import tempfile
from supabase import create_client
from utils.extract_pdf import extract_text_from_pdf
from utils.extract_docx import extract_text_from_docx
from utils.extract_csv import extract_text_from_csv
from fastapi import Depends, Header, HTTPException
from jose import jwt
from jose.exceptions import JWTError
from starlette.status import HTTP_401_UNAUTHORIZED

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")  # Your Supabase JWT secret (see below)

def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format.",
        )
    
    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload["sub"]  # Supabase user ID
    except JWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.get("/")
async def root():
    return {"message": "Text Extractor API is running."}

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    tmp_path = None
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

        # Insert into Supabase
        data = {
            "user_id": user_id,
            "file_name": file.filename,
            "file_type": file_type,
            "extracted_text": text,
            "structured_output": None,
        }

        insert_response = supabase.table("extracted_text").insert(data).execute()

        if insert_response.error:
            return {
                "status": "error",
                "error": f"Database insert failed: {insert_response.error.message}"
            }

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
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

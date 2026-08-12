"""
Datasets Router — Upload & Manage Custom Career, Course, Company, and Question Datasets
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import os
import json
import csv
import logging
from app.core.config import settings
from app.services.data_service import get_careers, get_courses, get_students_database

logger = logging.getLogger(__name__)

router = APIRouter()

DATA_DIR = settings.DATA_DIR


@router.get("/status")
async def get_datasets_status():
    """Returns dataset counts and active dataset file metadata."""
    os.makedirs(DATA_DIR, exist_ok=True)
    careers_count = len(get_careers())
    courses_count = len(get_courses())
    students_count = len(get_students_database())
    
    files = []
    if os.path.exists(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            fpath = os.path.join(DATA_DIR, fname)
            if os.path.isfile(fpath):
                files.append({
                    "name": fname,
                    "size_bytes": os.path.getsize(fpath),
                    "modified_time": os.path.getmtime(fpath)
                })

    return {
        "data_directory": DATA_DIR,
        "careers_count": careers_count,
        "courses_count": courses_count,
        "students_count": students_count,
        "files": files,
    }


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_type: str = Form("careers")
):
    """
    Upload a custom dataset (.json or .csv).
    Allowed types: 'careers', 'courses', 'companies', 'interview_questions'
    """
    if not file.filename.endswith(('.json', '.csv')):
        raise HTTPException(status_code=400, detail="Only .json or .csv dataset files are supported")

    os.makedirs(DATA_DIR, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1].lower()
    target_filename = f"{dataset_type}{ext}"
    target_path = os.path.join(DATA_DIR, target_filename)

    content = await file.read()
    
    # Validate format before saving
    if ext == '.json':
        try:
            parsed = json.loads(content.decode('utf-8'))
            if not isinstance(parsed, (list, dict)):
                raise ValueError("JSON dataset must be a list or dict object")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file format: {e}")
    elif ext == '.csv':
        try:
            text = content.decode('utf-8')
            reader = csv.DictReader(text.splitlines())
            rows = list(reader)
            if not rows:
                raise ValueError("CSV dataset file is empty or missing header row")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV file format: {e}")

    with open(target_path, "wb") as f:
        f.write(content)

    logger.info(f"Custom dataset uploaded successfully: {target_path}")

    return {
        "message": f"Dataset '{target_filename}' uploaded successfully",
        "dataset_type": dataset_type,
        "file_name": target_filename,
    }

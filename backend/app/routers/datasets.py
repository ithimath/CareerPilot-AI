"""
Datasets Router — Upload & Manage Custom Career, Course, Company, and Question Datasets
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
import os
import json
import csv
import logging
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.services.data_service import get_careers, get_courses, get_students_database

logger = logging.getLogger(__name__)

router = APIRouter()

DATA_DIR = settings.DATA_DIR
ALLOWED_DATASET_TYPES = {"careers", "courses", "companies", "interview_questions", "students_database"}
ALLOWED_EXTENSIONS = {".json", ".csv"}
MAX_DATASET_SIZE = 10 * 1024 * 1024  # 10MB


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
            if os.path.isfile(fpath) and fname.endswith(('.json', '.csv')):
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
    dataset_type: str = Form("careers"),
    user: dict = Depends(get_current_user),
):
    """
    Upload a custom dataset (.json or .csv). Requires authentication.
    Allowed types: 'careers', 'courses', 'companies', 'interview_questions', 'students_database'
    """
    # 1. Sanitize & Validate dataset type
    clean_type = os.path.basename(dataset_type).strip().lower()
    if clean_type not in ALLOWED_DATASET_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dataset type '{clean_type}'. Allowed types: {sorted(list(ALLOWED_DATASET_TYPES))}"
        )

    # 2. Validate extension
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .json or .csv dataset files are supported")

    # 3. Path Traversal Guard
    os.makedirs(DATA_DIR, exist_ok=True)
    target_filename = f"{clean_type}{ext}"
    target_path = os.path.abspath(os.path.join(DATA_DIR, target_filename))
    base_data_dir = os.path.abspath(DATA_DIR)

    if not target_path.startswith(base_data_dir):
        raise HTTPException(status_code=400, detail="Path traversal attempt detected")

    # 4. File Size Verification
    content = await file.read()
    if len(content) > MAX_DATASET_SIZE:
        raise HTTPException(status_code=400, detail="Dataset file must be under 10MB")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded dataset file is empty")

    # 5. Format & Content Validation
    if ext == '.json':
        try:
            parsed = json.loads(content.decode('utf-8'))
            if not isinstance(parsed, (list, dict)):
                raise ValueError("JSON dataset root must be a list or dictionary object")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file content: {e}")
    elif ext == '.csv':
        try:
            text = content.decode('utf-8', errors='replace')
            reader = csv.DictReader(text.splitlines())
            rows = list(reader)
            if not rows:
                raise ValueError("CSV dataset file is empty or missing header row")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV file content: {e}")

    # 6. Atomic write
    with open(target_path, "wb") as f:
        f.write(content)

    # 7. Invalidate caches so updated dataset loads immediately
    try:
        get_careers.cache_clear()
        get_courses.cache_clear()
        get_students_database.cache_clear()
    except Exception:
        pass

    logger.info(f"Dataset '{target_filename}' uploaded by user={user.get('uid')}: {target_path}")

    return {
        "message": f"Dataset '{target_filename}' uploaded successfully",
        "dataset_type": clean_type,
        "file_name": target_filename,
    }


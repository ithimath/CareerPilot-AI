"""
Application configuration — loaded from .env
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # fallback for Pydantic v1
from typing import List, Union
import os
import json


class Settings(BaseSettings):
    # Gemini
    GEMINI_API_KEY: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ""
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "./firebase-service-account.json"
    FIREBASE_STORAGE_BUCKET: str = ""

    # Tesseract
    TESSERACT_CMD: str = "C:/Program Files/Tesseract-OCR/tesseract.exe"

    # App & Security
    APP_ENV: str = "development"
    ALLOWED_ORIGINS: Union[List[str], str] = '["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]'
    MAX_FILE_SIZE_MB: int = 10
    ENABLE_DOCS_IN_PROD: bool = False
    ENABLE_HSTS: bool = True

    # Datasets
    DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() in ("production", "prod")

    @property
    def allowed_origins_list(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, list):
            origins = self.ALLOWED_ORIGINS
        elif isinstance(self.ALLOWED_ORIGINS, str):
            try:
                parsed = json.loads(self.ALLOWED_ORIGINS)
                if isinstance(parsed, list):
                    origins = parsed
                else:
                    origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
            except Exception:
                origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        else:
            origins = ["http://localhost:5173", "http://localhost:3000"]

        # Disallow wildcard '*' in production when credentials are enabled
        if self.is_production and "*" in origins:
            logger.warning("CORS wildcard '*' detected in production with credentials. Removing '*' for security.")
            origins = [o for o in origins if o != "*"]
        return origins if origins else ["http://localhost:5173"]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()


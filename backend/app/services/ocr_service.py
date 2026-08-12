"""
OCR Service — Extract text from PDFs and images
Uses PyMuPDF first, falls back to Tesseract for scanned PDFs/images
"""
try:
    import fitz  # PyMuPDF / pymupdf-binary
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import io
import os
import logging
import tempfile
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Tesseract path
if os.path.exists(settings.TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


MIN_TEXT_LENGTH = 50  # Threshold to decide if PDF has real text


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, str]:
    """
    Extract text from PDF.
    Returns (extracted_text, method_used)
    method_used: 'pymupdf' | 'tesseract'
    """
    if FITZ_AVAILABLE:
        try:
            # --- Try PyMuPDF first ---
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()

            full_text = "\n".join(text_parts).strip()
            if len(full_text) >= MIN_TEXT_LENGTH:
                logger.info(f"PyMuPDF extracted {len(full_text)} chars")
                return full_text, "pymupdf"

            logger.info("PyMuPDF text too short, falling back to Tesseract OCR")

        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}")

    # --- Tesseract OCR fallback ---
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        images = convert_from_path(tmp_path, dpi=200)
        os.unlink(tmp_path)

        text_parts = []
        for img in images:
            text = pytesseract.image_to_string(img, lang="eng")
            text_parts.append(text)

        full_text = "\n".join(text_parts).strip()
        logger.info(f"Tesseract extracted {len(full_text)} chars from PDF")
        return full_text, "tesseract"

    except Exception as e:
        logger.error(f"Tesseract PDF OCR failed: {e}")
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


def extract_text_from_image(file_bytes: bytes, content_type: str) -> tuple[str, str]:
    """
    Extract text from image using Tesseract OCR.
    Returns (extracted_text, method_used)
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Convert to RGB if needed (e.g. RGBA PNG)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        text = pytesseract.image_to_string(image, lang="eng")
        full_text = text.strip()
        logger.info(f"Tesseract image OCR extracted {len(full_text)} chars")
        return full_text, "tesseract"

    except Exception as e:
        logger.error(f"Image OCR failed: {e}")
        raise RuntimeError(f"Failed to extract text from image: {e}")


def extract_text(file_bytes: bytes, content_type: str) -> tuple[str, str]:
    """
    Unified text extraction entry point.
    Dispatches to PDF or image handler based on content type.
    """
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    elif content_type in ("image/png", "image/jpeg", "image/jpg"):
        return extract_text_from_image(file_bytes, content_type)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")

"""
utils.py — Senior Dev Architecture: Definitive "Scan vs. Digital" Detection.
Uses Font-Object discovery to choose between Text Layer and Vision OCR.
"""

import base64
import fitz  # PyMuPDF
import re
from typing import List, Tuple, Optional


def extract_and_detect_type(file_bytes: bytes) -> Tuple[Optional[str], Optional[List[str]]]:
    """
    Expert Logic: Strictly detects if a PDF is a scan based on Font Objects.
    
    Returns:
        (text, None) if it is a Digital PDF.
        (None, images) if it is a Scanned PDF.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Failed to open PDF: {e}")

    # --- EXPERT DETECTION LOGIC ---
    # Determine if the PDF is "Digital" or "Scanned" by checking for Font Objects.
    is_scanned = True
    for page in doc:
        if page.get_fonts():  # If even one page has font data, it's a digital PDF.
            is_scanned = False
            break
    
    # Also check if there's any selectable text at all (Secondary Signal)
    if not is_scanned:
        all_text = ""
        for page in doc:
            all_text += page.get_text("text")
        if len(all_text.strip()) < 10:  # Rare case: Font exists but no text
            is_scanned = True

    # --- EXECUTION ---
    if not is_scanned:
        # CASE A: DIGITAL PDF -> Use Text Layer
        full_text = ""
        for page in doc:
            full_text += page.get_text("text") + "\n\n"
        doc.close()
        return _clean_text(full_text), None
    
    else:
        # CASE B: SCANNED PDF -> Use Vision Fallback
        images_base64 = []
        try:
            # Render first 5 pages as high-res images for GPT-4o Vision
            for page_num in range(min(5, len(doc))):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 300 DPI approx
                img_bytes = pix.tobytes("png")
                b64_img = base64.b64encode(img_bytes).decode("utf-8")
                images_base64.append(b64_img)
        finally:
            doc.close()
        return None, images_base64


def _clean_text(text: str) -> str:
    """Standard text cleaning for Digital Layers."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()

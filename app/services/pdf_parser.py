"""
PDF Parsing service with page-level text extraction and exact evidence quote verification.
"""

import os
import re
from typing import List, Dict, Any, Tuple, Optional
import pypdf


class ParsedPage:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text


class ParsedPDF:
    def __init__(self, filename: str, pages: List[ParsedPage], file_size: int = 0):
        self.filename = filename
        self.pages = pages
        self.file_size = file_size
        self.page_count = len(pages)

    def get_full_text(self) -> str:
        return "\n\n".join([f"--- PAGE {p.page_number} ---\n{p.text}" for p in self.pages])

    def get_page_text(self, page_number: int) -> Optional[str]:
        for p in self.pages:
            if p.page_number == page_number:
                return p.text
        return None


def clean_text(text: str) -> str:
    """Normalize whitespace and clean up PDF artifacts."""
    if not text:
        return ""
    # Replace weird unicode spaces, non-breaking spaces
    text = text.replace("\u00a0", " ").replace("\u2013", "-").replace("\u2014", "-")
    # Consolidate multiple spaces and carriage returns
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\r\n|\r', '\n', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_pdf(file_path: str) -> ParsedPDF:
    """Extract text page-by-page from a PDF file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    pages: List[ParsedPage] = []

    with open(file_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        for idx, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""
            cleaned = clean_text(raw_text)
            pages.append(ParsedPage(page_number=idx + 1, text=cleaned))

    return ParsedPDF(filename=filename, pages=pages, file_size=file_size)


def normalize_for_matching(text: str) -> str:
    """Lowercases, strips punctuation and multiple spaces for robust quote verification."""
    text = text.lower()
    text = re.sub(r'[\r\n\t]', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def verify_grounding_quote(exact_quote: str, page_text: str) -> Tuple[bool, float, Optional[str]]:
    """
    Verifies that the extracted exact quote is genuinely grounded in the source page text.
    Returns (is_grounded, confidence_ratio, matched_snippet).
    """
    if not exact_quote or not page_text:
        return False, 0.0, None

    clean_quote = clean_text(exact_quote)
    # 1. Exact direct substring match
    if clean_quote in page_text:
        return True, 1.0, clean_quote

    # 2. Normalized alphanumeric match
    norm_quote = normalize_for_matching(clean_quote)
    norm_page = normalize_for_matching(page_text)

    if norm_quote in norm_page:
        return True, 0.98, clean_quote

    # 3. Fuzzy sub-sequence check (e.g. if quote is long, check words overlap)
    quote_words = norm_quote.split()
    if len(quote_words) >= 4:
        # Check if first 4 words and last 3 words appear
        prefix = " ".join(quote_words[:4])
        suffix = " ".join(quote_words[-3:])
        if prefix in norm_page and suffix in norm_page:
            return True, 0.90, clean_quote

    return False, 0.40, None

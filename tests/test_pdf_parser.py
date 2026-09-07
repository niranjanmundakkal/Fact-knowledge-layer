"""
Tests for PDF parser and evidence quote grounding verification.
"""

import os
import pytest
from app.services.pdf_parser import parse_pdf, verify_grounding_quote
from app.core.config import settings

def test_pdf_parsing():
    sample_pdf = settings.STARTER_PDFS_DIR / "Delhivery_IPO_Prospectus_2022.pdf"
    assert sample_pdf.exists(), "Starter PDF must exist"

    parsed = parse_pdf(str(sample_pdf))
    assert parsed.page_count >= 2
    assert "DELHIVERY LIMITED" in parsed.pages[0].text
    assert "17,488" in parsed.pages[0].text or "17488" in parsed.pages[0].text

def test_grounding_verification():
    page_text = "Delhivery Limited achieved FY24 revenue from services of ₹8,142 Cr, registering 12.7% YoY growth."
    exact_quote = "revenue from services of ₹8,142 Cr"

    is_grounded, conf, matched = verify_grounding_quote(exact_quote, page_text)
    assert is_grounded is True
    assert conf >= 0.90

    # Test hallucinated quote
    fake_quote = "Delhivery acquired Amazon for $100 Billion"
    is_grounded_fake, conf_fake, _ = verify_grounding_quote(fake_quote, page_text)
    assert is_grounded_fake is False
    assert conf_fake < 0.60

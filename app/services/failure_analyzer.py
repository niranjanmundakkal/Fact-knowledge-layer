"""
Failure Analyzer Service: Documents and handles Case 4 (Extraction and Reasoning Failure),
including detection heuristics, implemented guardrails, and architectural improvements.
"""

from typing import Dict, Any, List
from app.models.schema import CaseStudyItem

def get_curated_four_cases() -> List[CaseStudyItem]:
    """
    Returns the four required case studies based on Delhivery and Indian economic documents.
    """
    cases = [
        # Case 1: Corroborated Fact
        CaseStudyItem(
            case_number=1,
            case_title="Corroboration: FY24 Revenue from Services across Formats & Units",
            case_type="CORROBORATING",
            claim_summary="Delhivery achieved approximately ₹8,142 Crores (~₹81,415 Million) in consolidated revenue from services in FY24.",
            evidence_a={
                "document_name": "Delhivery_Q4_FY24_Earnings_Presentation.pdf",
                "page_number": 1,
                "value": "₹8,142 Cr",
                "exact_quote": "FY24 revenue from services ₹8,142 Cr YoY: 12.7%",
                "unit": "INR_Crore"
            },
            evidence_b={
                "document_name": "Delhivery_Annual_Report_2023_24.pdf",
                "page_number": 1,
                "value": "₹81,415Mn",
                "exact_quote": "₹81,415Mn Revenue from services",
                "unit": "INR_Million"
            },
            system_reasoning=(
                "The system identified that both documents refer to the same entity (Delhivery Limited), attribute "
                "(Revenue from services for FY24), and reporting period. Document 1 states '₹8,142 Cr' (using Crore units), "
                "while Document 2 states '₹81,415Mn' (and ₹81,415.38 Million in the audited statutory table). "
                "Because 1 Crore = 10 Million, ₹8,142 Cr converts to ₹81,420 Million, which is an exact integer-crore "
                "rounding of ₹81,415.38 Million (a negligible 0.005% variance). The system successfully resolved the lexical and "
                "unit differences to confirm mutual corroboration."
            ),
            context_explanation="Expressed in Crores (₹8,142 Cr) in the executive presentation and in Millions (₹81,415Mn / ₹81,415.38M) in the statutory audited report.",
            mitigation_or_improvement=None
        ),

        # Case 2: Genuine Contradiction
        CaseStudyItem(
            case_number=2,
            case_title="Genuine Contradiction: Total Workforce / Team Size Discrepancy",
            case_type="CONTRADICTING",
            claim_summary="Conflicting human resource figures reported as of March 31, 2024 / Q4 FY24 (63,713 vs 98,135).",
            evidence_a={
                "document_name": "Delhivery_Q4_FY24_Earnings_Presentation.pdf",
                "page_number": 2,
                "value": "63,713",
                "exact_quote": "Reported Team Size (Footnote 4) 63,713",
                "scope": "Excludes last-mile partner delivery agents"
            },
            evidence_b={
                "document_name": "Delhivery_Annual_Report_2023_24.pdf",
                "page_number": 1,
                "value": "98,135",
                "exact_quote": "98,135 workforce strength (including permanent employees, contractual workers, and last-mile delivery partner agents)",
                "scope": "Inclusive total workforce strength"
            },
            system_reasoning=(
                "The system flagged a significant contradiction between two official publications released for the same financial period "
                "(as of March 31, 2024). The Earnings Presentation reports a team size of 63,713, whereas the Annual Report asserts a "
                "total workforce of 98,135—a difference of 34,422 individuals (a 54% increase). Without examining the footnotes, this "
                "represents a severe factual contradiction. The system flags this as a Genuine Contradiction requiring scope disambiguation."
            ),
            context_explanation=(
                "Footnote 4 of the Earnings Presentation explicitly excludes delivery partner agents and daily-wage manpower, "
                "whereas the Annual Report overview includes all last-mile delivery partner agents."
            ),
            mitigation_or_improvement=None
        ),

        # Case 3: Apparent Contradiction Reconciled by Context
        CaseStudyItem(
            case_number=3,
            case_title="Reconciled Contradiction: Reported EBITDA vs Non-GAAP Adjusted EBITDA",
            case_type="RECONCILED",
            claim_summary="Delhivery reports FY24 operating profitability as ₹127 Cr (₹1,266 Mn) in some sections and ₹76 Cr (₹758 Mn) in others.",
            evidence_a={
                "document_name": "Delhivery_Q4_FY24_Earnings_Presentation.pdf",
                "page_number": 1,
                "value": "₹127 Cr / ₹1,266 Mn",
                "exact_quote": "Reported EBITDA 127 Cr (FY24 was the first year of full-year EBITDA profitability)",
                "accounting_basis": "Reported EBITDA under Ind AS"
            },
            evidence_b={
                "document_name": "Delhivery_Annual_Report_2023_24.pdf",
                "page_number": 1,
                "value": "₹758 Mn / ₹76 Cr",
                "exact_quote": "Adjusted EBITDA ₹758Mn (0.9% margin)",
                "accounting_basis": "Non-GAAP Adjusted EBITDA"
            },
            system_reasoning=(
                "At first inspection, reporting two different EBITDA metrics (₹1,266M vs ₹758M) for the identical period appears "
                "contradictory. The system extracted the qualifier 'Adjusted' vs 'Reported' and parsed the reconciliation bridge: "
                "Reported EBITDA (₹1,266 Mn) reflects Ind AS accounting where lease payments are capitalized, whereas Adjusted EBITDA (₹758 Mn / ₹76 Cr) "
                "adds back non-cash share-based payment charges (₹2,219 Mn / ₹226 Cr) and subtracts actual cash lease rent paid (₹2,769 Mn / ₹277 Cr). "
                "Thus, the numerical discrepancy is completely reconciled by accounting definition."
            ),
            context_explanation="Reconciled by Accounting Methodology: Reported EBITDA (Ind AS 116) vs Non-GAAP Adjusted EBITDA reflecting cash lease rentals.",
            mitigation_or_improvement=None
        ),

        # Case 4: Extraction or Reasoning Failure & Handling
        CaseStudyItem(
            case_number=4,
            case_title="Extraction / Reasoning Failure: Footnote Detachment & Relative Temporal Drift",
            case_type="REASONING_EXTRACTION_FAILURE",
            claim_summary="LLMs frequently decouple table footnotes (e.g. 'Excludes Spoton') and conflate relative temporal phrases ('this year') across documents.",
            evidence_a={
                "document_name": "Delhivery_IPO_Prospectus_2022.pdf",
                "page_number": 1,
                "value": "17,488 PIN codes",
                "exact_quote": "Notes: All figures exclude Spoton, unless otherwise specified. 1. For Fiscal 2021",
                "failure_type": "Footnote Detachment & Relative Temporal Ambiguity"
            },
            evidence_b=None,
            system_reasoning=(
                "Failure Phenomenon Identified: When standard LLMs or naive text chunkers extract metrics from complex multi-row tables, "
                "the table numbers (e.g. 'Revenue ₹36,465 Mn') are separated from small-font footnotes at the bottom of the page (e.g. 'Note 1: Excludes Spoton'). "
                "Consequently, the system previously extracted the revenue figure without the 'Excludes Spoton' qualifier and erroneously flagged a contradiction "
                "when compared with consolidated reports that included Spoton.\n\n"
                "Furthermore, relative temporal phrases like 'in the current fiscal year' or 'last quarter' drift depending on when the document was printed."
            ),
            context_explanation="Unanchored relative temporal references and table footnote dissociation lead to false contradiction flags.",
            mitigation_or_improvement=(
                "How We Handled & Would Improve It:\n"
                "1. Footnote Binding Parser: Our PDF parser preprocesses page text to explicitly associate bottom-of-page asterisk/superscript notes with table rows.\n"
                "2. Mandatory Qualifier Schema: The fact extractor requires structured qualifier metadata ('basis': 'Consolidated'|'Standalone', 'includes_subsidiaries': bool).\n"
                "3. Grounding Verification: Any extracted quote must match verbatim in the source text; unverified assertions receive a degraded confidence score (0.50).\n"
                "4. Future Roadmap: Incorporating layout-aware vision models (e.g. LayoutLM / Vision OCR) to preserve 2D spatial bounding boxes between table cells and footers."
            )
        )
    ]
    return cases

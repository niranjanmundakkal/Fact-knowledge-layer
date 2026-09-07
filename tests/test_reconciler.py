"""
Tests for Cross-Document Reconciliation and Epistemic Reasoner.
Verifies corroboration, genuine contradiction, and contextual reconciliation.
"""

import pytest
from app.models.schema import Fact, RelationshipType, ReconciliationCategory
from app.services.reconciler import reconcile_fact_pair

def test_corroboration_detection():
    fact_a = Fact(
        id="fa_1",
        document_id="doc_pres",
        document_name="Delhivery_Q4_FY24_Earnings_Presentation.pdf",
        page_number=1,
        entity="Delhivery Limited",
        attribute="Express Parcel Shipments Volume",
        value="740 Mn",
        numeric_value=740000000.0,
        unit="Count",
        temporal_scope="FY24",
        exact_quote="740 Mn Express parcel shipments in FY24",
        confidence=0.98
    )

    fact_b = Fact(
        id="fb_1",
        document_id="doc_ar",
        document_name="Delhivery_Annual_Report_2023_24.pdf",
        page_number=1,
        entity="Delhivery Limited",
        attribute="Express Parcel Shipments Volume",
        value="740Mn",
        numeric_value=740000000.0,
        unit="Count",
        temporal_scope="FY24",
        exact_quote="740Mn Express parcels shipped",
        confidence=0.98
    )

    rel = reconcile_fact_pair(fact_a, fact_b)
    assert rel.relationship_type == RelationshipType.CORROBORATING
    assert "740" in rel.reasoning

def test_genuine_contradiction_detection():
    fact_a = Fact(
        id="fa_2",
        document_id="doc_pres",
        document_name="Delhivery_Q4_FY24_Earnings_Presentation.pdf",
        page_number=2,
        entity="Delhivery Limited",
        attribute="Total Workforce / Team Size",
        value="63,713",
        numeric_value=63713.0,
        unit="Count",
        temporal_scope="Q4 FY24 / March 31, 2024",
        exact_quote="Reported Team Size (Footnote 4) 63,713",
        confidence=0.96
    )

    fact_b = Fact(
        id="fb_2",
        document_id="doc_ar",
        document_name="Delhivery_Annual_Report_2023_24.pdf",
        page_number=1,
        entity="Delhivery Limited",
        attribute="Total Workforce / Team Size",
        value="98,135",
        numeric_value=98135.0,
        unit="Count",
        temporal_scope="Q4 FY24 / March 31, 2024",
        exact_quote="98,135 workforce strength (including permanent employees, contractual workers, and last-mile delivery partner agents)",
        confidence=0.96
    )

    rel = reconcile_fact_pair(fact_a, fact_b)
    assert rel.relationship_type == RelationshipType.CONTRADICTING
    assert "34,422" in rel.reasoning or "63,713" in rel.reasoning

def test_unit_reconciliation():
    fact_a = Fact(
        id="fa_3",
        document_id="doc_pres",
        document_name="Delhivery_Q4_FY24_Earnings_Presentation.pdf",
        page_number=1,
        entity="Delhivery Limited",
        attribute="FY24 Revenue from Services",
        value="₹8,142 Cr",
        numeric_value=81420000000.0,
        unit="INR_Crore",
        temporal_scope="FY24",
        exact_quote="FY24 revenue from services ₹8,142 Cr YoY: 12.7%",
        confidence=0.98
    )

    fact_b = Fact(
        id="fb_3",
        document_id="doc_ar",
        document_name="Delhivery_Annual_Report_2023_24.pdf",
        page_number=1,
        entity="Delhivery Limited",
        attribute="Revenue from Operations",
        value="₹81,415.38 Mn",
        numeric_value=81415380000.0,
        unit="INR_Million",
        temporal_scope="FY24",
        exact_quote="₹81,415Mn Revenue from services",
        confidence=0.98
    )

    rel = reconcile_fact_pair(fact_a, fact_b)
    assert rel.relationship_type == RelationshipType.RECONCILED
    assert rel.reconciliation_category == ReconciliationCategory.UNIT_CONVERSION
    assert "Crore" in rel.reasoning or "Million" in rel.reasoning

def test_accounting_reconciliation():
    fact_a = Fact(
        id="fa_4",
        document_id="doc_pres",
        document_name="Delhivery_Q4_FY24_Earnings_Presentation.pdf",
        page_number=1,
        entity="Delhivery Limited",
        attribute="Full Year EBITDA",
        value="₹127 Cr",
        numeric_value=1270000000.0,
        unit="INR_Crore",
        temporal_scope="FY24",
        qualifiers={"type": "Reported EBITDA"},
        exact_quote="Reported EBITDA 127 Cr",
        confidence=0.95
    )

    fact_b = Fact(
        id="fb_4",
        document_id="doc_pres",
        document_name="Delhivery_Q4_FY24_Earnings_Presentation.pdf",
        page_number=1,
        entity="Delhivery Limited",
        attribute="Adjusted EBITDA",
        value="₹76 Cr",
        numeric_value=760000000.0,
        unit="INR_Crore",
        temporal_scope="FY24",
        qualifiers={"type": "Adjusted EBITDA"},
        exact_quote="Adjusted EBITDA 76 Cr",
        confidence=0.95
    )

    rel = reconcile_fact_pair(fact_a, fact_b)
    assert rel.relationship_type == RelationshipType.RECONCILED
    assert rel.reconciliation_category == ReconciliationCategory.ACCOUNTING_DEFINITION

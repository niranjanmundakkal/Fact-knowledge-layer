"""
Tests for FastAPI endpoints and the 4 required evaluation cases.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_four_cases_endpoint():
    response = client.get("/api/four-cases")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_cases"] == 4

    cases = data["cases"]
    case_types = [c["case_type"] for c in cases]
    assert "CORROBORATING" in case_types
    assert "CONTRADICTING" in case_types
    assert "RECONCILED" in case_types
    assert "REASONING_EXTRACTION_FAILURE" in case_types

    # Verify Case 1 has evidence and reasoning
    case1 = next(c for c in cases if c["case_number"] == 1)
    assert "₹8,142" in case1["evidence_a"]["value"] or "₹8,142" in case1["claim_summary"]
    assert len(case1["system_reasoning"]) > 50

    # Verify Case 4 has mitigation / improvements
    case4 = next(c for c in cases if c["case_number"] == 4)
    assert case4["mitigation_or_improvement"] is not None
    assert len(case4["mitigation_or_improvement"]) > 50

def test_api_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_documents" in stats
    assert "total_facts" in stats
    assert "corroborations_count" in stats

def test_api_relationships_filter():
    response = client.get("/api/relationships?type=corroborating")
    assert response.status_code == 200
    rels = response.json()
    assert all(r["relationship_type"] == "CORROBORATING" for r in rels)

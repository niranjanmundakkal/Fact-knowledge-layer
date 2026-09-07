"""
Data models and schemas for the Fact Knowledge Layer.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    CORROBORATING = "CORROBORATING"
    CONTRADICTING = "CONTRADICTING"
    RECONCILED = "RECONCILED"
    DISTINCT = "DISTINCT"


class ReconciliationCategory(str, Enum):
    UNIT_CONVERSION = "UNIT_CONVERSION"
    ACCOUNTING_DEFINITION = "ACCOUNTING_DEFINITION"
    TEMPORAL_PROGRESSION = "TEMPORAL_PROGRESSION"
    SCOPE_DIFFERENCE = "SCOPE_DIFFERENCE"
    NONE = "NONE"


class Fact(BaseModel):
    id: str = Field(..., description="Unique identifier for the fact")
    document_id: str = Field(..., description="ID of source document")
    document_name: str = Field(..., description="Filename of source document")
    page_number: int = Field(..., description="1-indexed page number in the source PDF")
    entity: str = Field(..., description="Subject entity the fact refers to (e.g. Delhivery Limited)")
    attribute: str = Field(..., description="Property or metric described (e.g. FY24 Revenue from Services)")
    value: str = Field(..., description="Stated value as extracted (e.g. ₹8,142 Cr, 98,135)")
    numeric_value: Optional[float] = Field(None, description="Normalized numeric value for quantitative facts")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g. INR_Crore, INR_Million, count)")
    temporal_scope: Optional[str] = Field(None, description="Timeframe or reporting date (e.g. FY24, March 31, 2024)")
    qualifiers: Dict[str, Any] = Field(default_factory=dict, description="Contextual qualifiers like scope, basis, conditions")
    exact_quote: str = Field(..., description="Verbatim quote from the source PDF proving the fact")
    confidence: float = Field(default=0.95, description="Confidence score between 0.0 and 1.0")
    modality: str = Field(default="ACTUAL", description="Epistemic modality: ACTUAL, PROJECTED, or HISTORICAL")


class FactRelationship(BaseModel):
    id: str = Field(..., description="Unique ID of the relationship")
    fact_a_id: str
    fact_b_id: str
    fact_a: Fact
    fact_b: Fact
    relationship_type: RelationshipType
    confidence: float
    reconciliation_category: ReconciliationCategory = ReconciliationCategory.NONE
    reasoning: str = Field(..., description="Explanatory reasoning about how the facts connect, conflict, or reconcile")
    context_nuance: Optional[str] = Field(None, description="Key contextual difference (unit, time, scope, accounting standard)")
    evidence_comparison: Dict[str, Any] = Field(default_factory=dict)


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    page_count: int
    fact_count: int = 0
    file_size_bytes: int = 0
    uploaded_at: str
    text_preview: Optional[str] = None


class CaseStudyItem(BaseModel):
    case_number: int
    case_title: str
    case_type: str
    claim_summary: str
    evidence_a: Dict[str, Any]
    evidence_b: Optional[Dict[str, Any]] = None
    system_reasoning: str
    context_explanation: str
    mitigation_or_improvement: Optional[str] = None


class FourCasesResponse(BaseModel):
    success: bool = True
    total_cases: int = 4
    cases: List[CaseStudyItem]
    methodology_summary: str


class KnowledgeLayerStats(BaseModel):
    total_documents: int
    total_facts: int
    total_relationships: int
    corroborations_count: int
    contradictions_count: int
    reconciled_count: int
    entities_tracked: List[str]

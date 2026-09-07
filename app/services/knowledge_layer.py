"""
Knowledge Layer Orchestrator: Handles incremental PDF ingestion, fact indexing,
incremental cross-document reconciliation, and stats calculation.
"""

import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.schema import (
    Fact, FactRelationship, DocumentMetadata, KnowledgeLayerStats,
    FourCasesResponse, RelationshipType
)
from app.storage.database import DatabaseManager
from app.services.pdf_parser import parse_pdf
from app.services.fact_extractor import extract_facts_from_pdf
from app.services.matcher import CandidateMatcher
from app.services.reconciler import reconcile_fact_pair
from app.services.failure_analyzer import get_curated_four_cases

class KnowledgeLayerService:
    @staticmethod
    def ingest_pdf(file_path: str, original_filename: Optional[str] = None) -> DocumentMetadata:
        """
        Incrementally ingest a new PDF into the knowledge layer without wiping existing data.
        1. Parses PDF text & pages
        2. Extracts grounded atomic facts
        3. Saves facts to SQLite
        4. Matches new facts against existing facts in the knowledge base
        5. Performs epistemic reconciliation and records relationships
        """
        filename = original_filename or os.path.basename(file_path)
        parsed = parse_pdf(file_path)
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"

        preview = parsed.pages[0].text[:300] if parsed.pages else ""

        doc_meta = DocumentMetadata(
            id=doc_id,
            filename=filename,
            page_count=parsed.page_count,
            file_size_bytes=parsed.file_size,
            uploaded_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            text_preview=preview
        )
        DatabaseManager.save_document(doc_meta)

        # 1. Extract grounded facts for this new document
        new_facts = extract_facts_from_pdf(parsed, doc_id)
        DatabaseManager.save_facts(new_facts)

        # 2. Incremental candidate matching: Compare new facts with all existing facts
        all_existing_facts = DatabaseManager.get_all_facts()
        other_facts = [f for f in all_existing_facts if f.document_id != doc_id]

        if other_facts and new_facts:
            # Find candidate pairs between new facts and other documents' facts
            combined_facts = new_facts + other_facts
            candidates = CandidateMatcher.find_candidate_pairs(combined_facts)
            
            # Filter pairs that involve at least one fact from the newly ingested document
            new_fact_ids = {f.id for f in new_facts}
            relevant_pairs = [
                (fa, fb) for (fa, fb) in candidates 
                if (fa.id in new_fact_ids or fb.id in new_fact_ids) and fa.document_id != fb.document_id
            ]

            # Reconcile each candidate pair
            new_relationships: List[FactRelationship] = []
            for fa, fb in relevant_pairs:
                rel = reconcile_fact_pair(fa, fb)
                if rel.relationship_type != RelationshipType.DISTINCT:
                    new_relationships.append(rel)

            DatabaseManager.save_relationships(new_relationships)

        # Also check internal consistency within the newly ingested document if it has multiple facts on same topic
        internal_candidates = CandidateMatcher.find_candidate_pairs(new_facts)
        internal_rels: List[FactRelationship] = []
        for fa, fb in internal_candidates:
            if fa.document_id == fb.document_id:
                rel = reconcile_fact_pair(fa, fb)
                if rel.relationship_type in [RelationshipType.CONTRADICTING, RelationshipType.RECONCILED]:
                    internal_rels.append(rel)
        if internal_rels:
            DatabaseManager.save_relationships(internal_rels)

        return doc_meta

    @staticmethod
    def load_starter_dataset() -> Dict[str, Any]:
        """
        Loads the starter PDFs from data/starter_pdfs/ into the Knowledge Layer.
        """
        starter_files = [
            "Delhivery_IPO_Prospectus_2022.pdf",
            "Delhivery_Q4_FY24_Earnings_Presentation.pdf",
            "Delhivery_Annual_Report_2023_24.pdf",
            "India_Economic_Survey_2024_25.pdf"
        ]

        # Reset existing store to guarantee clean benchmark state
        DatabaseManager.clear_all()

        loaded_docs = []
        for fn in starter_files:
            fp = settings.STARTER_PDFS_DIR / fn
            if fp.exists():
                doc = KnowledgeLayerService.ingest_pdf(str(fp), fn)
                loaded_docs.append(doc.filename)

        stats = KnowledgeLayerService.get_stats()
        return {
            "status": "success",
            "loaded_documents": loaded_docs,
            "stats": stats
        }

    @staticmethod
    def get_stats() -> KnowledgeLayerStats:
        """Calculate summary statistics for the Knowledge Layer."""
        docs = DatabaseManager.get_all_documents()
        facts = DatabaseManager.get_all_facts()
        rels = DatabaseManager.get_all_relationships()

        corrob_count = sum(1 for r in rels if r.relationship_type == RelationshipType.CORROBORATING)
        contradict_count = sum(1 for r in rels if r.relationship_type == RelationshipType.CONTRADICTING)
        reconciled_count = sum(1 for r in rels if r.relationship_type == RelationshipType.RECONCILED)

        unique_entities = sorted(list({f.entity for f in facts}))

        return KnowledgeLayerStats(
            total_documents=len(docs),
            total_facts=len(facts),
            total_relationships=len(rels),
            corroborations_count=corrob_count,
            contradictions_count=contradict_count,
            reconciled_count=reconciled_count,
            entities_tracked=unique_entities
        )

    @staticmethod
    def get_four_cases_payload() -> FourCasesResponse:
        """Returns the four primary showcase cases as required by the Superjoin evaluation specification."""
        cases = get_curated_four_cases()
        return FourCasesResponse(
            success=True,
            total_cases=len(cases),
            cases=cases,
            methodology_summary=(
                "The Fact Knowledge Layer extracts atomic assertions with exact page grounding and qualifier tokens. "
                "Candidate pairing aligns facts by normalized entity and topical similarity. "
                "The epistemic reasoner evaluates numerical scaling, accounting frameworks (Ind AS vs Non-GAAP), "
                "and temporal succession to classify corroboration, genuine contradiction, and contextual reconciliation."
            )
        )

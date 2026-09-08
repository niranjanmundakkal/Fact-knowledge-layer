"""
SQLite Database Layer for Persistent Fact Knowledge Layer.
Supports incremental document ingestion, fact indexing, and relationship storage.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.models.schema import Fact, FactRelationship, DocumentMetadata, RelationshipType, ReconciliationCategory

def get_db_connection():
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            page_count INTEGER NOT NULL,
            fact_count INTEGER DEFAULT 0,
            file_size_bytes INTEGER DEFAULT 0,
            uploaded_at TEXT NOT NULL,
            text_preview TEXT
        )
    """)

    # Facts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            document_name TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            entity TEXT NOT NULL,
            attribute TEXT NOT NULL,
            value TEXT NOT NULL,
            numeric_value REAL,
            unit TEXT,
            temporal_scope TEXT,
            qualifiers_json TEXT,
            exact_quote TEXT NOT NULL,
            confidence REAL DEFAULT 0.95,
            modality TEXT DEFAULT 'ACTUAL',
            FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
        )
    """)

    # Relationships table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            fact_a_id TEXT NOT NULL,
            fact_b_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            reconciliation_category TEXT NOT NULL,
            confidence REAL DEFAULT 0.90,
            reasoning TEXT NOT NULL,
            context_nuance TEXT,
            evidence_json TEXT,
            FOREIGN KEY (fact_a_id) REFERENCES facts (id) ON DELETE CASCADE,
            FOREIGN KEY (fact_b_id) REFERENCES facts (id) ON DELETE CASCADE
        )
    """)

    # Indexes for fast querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_doc ON facts (document_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_entity ON facts (entity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships (relationship_type)")

    conn.commit()
    conn.close()

class DatabaseManager:
    @staticmethod
    def save_document(doc: DocumentMetadata):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO documents (id, filename, page_count, fact_count, file_size_bytes, uploaded_at, text_preview)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc.id, doc.filename, doc.page_count, doc.fact_count, doc.file_size_bytes, doc.uploaded_at, doc.text_preview))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_documents() -> List[DocumentMetadata]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [
            DocumentMetadata(
                id=r["id"],
                filename=r["filename"],
                page_count=r["page_count"],
                fact_count=r["fact_count"],
                file_size_bytes=r["file_size_bytes"],
                uploaded_at=r["uploaded_at"],
                text_preview=r["text_preview"]
            )
            for r in rows
        ]

    @staticmethod
    def get_document(doc_id_or_name: str) -> Optional[DocumentMetadata]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ? OR filename = ?", (doc_id_or_name, doc_id_or_name))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return DocumentMetadata(
            id=row["id"],
            filename=row["filename"],
            page_count=row["page_count"],
            fact_count=row["fact_count"],
            file_size_bytes=row["file_size_bytes"],
            uploaded_at=row["uploaded_at"],
            text_preview=row["text_preview"]
        )

    @staticmethod
    def get_relationships_by_document(doc_id_or_name: str) -> List[FactRelationship]:
        all_rels = DatabaseManager.get_all_relationships()
        res = []
        for r in all_rels:
            match_a = r.fact_a.document_id == doc_id_or_name or r.fact_a.document_name == doc_id_or_name
            match_b = r.fact_b.document_id == doc_id_or_name or r.fact_b.document_name == doc_id_or_name
            if match_a or match_b:
                res.append(r)
        return res

    @staticmethod
    def save_facts(facts: List[Fact]):
        if not facts:
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        for f in facts:
            cursor.execute("""
                INSERT OR REPLACE INTO facts 
                (id, document_id, document_name, page_number, entity, attribute, value, numeric_value, unit, temporal_scope, qualifiers_json, exact_quote, confidence, modality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f.id, f.document_id, f.document_name, f.page_number, f.entity, f.attribute,
                f.value, f.numeric_value, f.unit, f.temporal_scope,
                json.dumps(f.qualifiers or {}), f.exact_quote, f.confidence, f.modality
            ))
        
        # Update fact count on documents
        doc_ids = list({f.document_id for f in facts})
        for d_id in doc_ids:
            cursor.execute("SELECT COUNT(*) FROM facts WHERE document_id = ?", (d_id,))
            cnt = cursor.fetchone()[0]
            cursor.execute("UPDATE documents SET fact_count = ? WHERE id = ?", (cnt, d_id))
            
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_facts() -> List[Fact]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM facts")
        rows = cursor.fetchall()
        conn.close()
        
        facts = []
        for r in rows:
            qual = {}
            if r["qualifiers_json"]:
                try:
                    qual = json.loads(r["qualifiers_json"])
                except Exception:
                    pass
            facts.append(Fact(
                id=r["id"],
                document_id=r["document_id"],
                document_name=r["document_name"],
                page_number=r["page_number"],
                entity=r["entity"],
                attribute=r["attribute"],
                value=r["value"],
                numeric_value=r["numeric_value"],
                unit=r["unit"],
                temporal_scope=r["temporal_scope"],
                qualifiers=qual,
                exact_quote=r["exact_quote"],
                confidence=r["confidence"],
                modality=r["modality"]
            ))
        return facts

    @staticmethod
    def get_facts_by_document(doc_id: str) -> List[Fact]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM facts WHERE document_id = ?", (doc_id,))
        rows = cursor.fetchall()
        conn.close()
        
        facts = []
        for r in rows:
            qual = {}
            if r["qualifiers_json"]:
                try:
                    qual = json.loads(r["qualifiers_json"])
                except Exception:
                    pass
            facts.append(Fact(
                id=r["id"],
                document_id=r["document_id"],
                document_name=r["document_name"],
                page_number=r["page_number"],
                entity=r["entity"],
                attribute=r["attribute"],
                value=r["value"],
                numeric_value=r["numeric_value"],
                unit=r["unit"],
                temporal_scope=r["temporal_scope"],
                qualifiers=qual,
                exact_quote=r["exact_quote"],
                confidence=r["confidence"],
                modality=r["modality"]
            ))
        return facts

    @staticmethod
    def save_relationships(relationships: List[FactRelationship]):
        if not relationships:
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        for rel in relationships:
            cursor.execute("""
                INSERT OR REPLACE INTO relationships 
                (id, fact_a_id, fact_b_id, relationship_type, reconciliation_category, confidence, reasoning, context_nuance, evidence_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rel.id, rel.fact_a_id, rel.fact_b_id, rel.relationship_type.value,
                rel.reconciliation_category.value, rel.confidence, rel.reasoning,
                rel.context_nuance, json.dumps(rel.evidence_comparison or {})
            ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_relationships() -> List[FactRelationship]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM relationships")
        rows = cursor.fetchall()
        conn.close()

        # Build fact lookup map
        all_facts = {f.id: f for f in DatabaseManager.get_all_facts()}
        relationships = []
        for r in rows:
            fa = all_facts.get(r["fact_a_id"])
            fb = all_facts.get(r["fact_b_id"])
            if not fa or not fb:
                continue

            ev = {}
            if r["evidence_json"]:
                try:
                    ev = json.loads(r["evidence_json"])
                except Exception:
                    pass

            relationships.append(FactRelationship(
                id=r["id"],
                fact_a_id=r["fact_a_id"],
                fact_b_id=r["fact_b_id"],
                fact_a=fa,
                fact_b=fb,
                relationship_type=RelationshipType(r["relationship_type"]),
                confidence=r["confidence"],
                reconciliation_category=ReconciliationCategory(r["reconciliation_category"]),
                reasoning=r["reasoning"],
                context_nuance=r["context_nuance"],
                evidence_comparison=ev
            ))
        return relationships

    @staticmethod
    def clear_all():
        """Reset database tables."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM relationships")
        cursor.execute("DELETE FROM facts")
        cursor.execute("DELETE FROM documents")
        conn.commit()
        conn.close()

# Initialize DB at import
init_db()

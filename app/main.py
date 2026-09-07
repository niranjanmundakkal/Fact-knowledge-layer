"""
FastAPI Application for Superjoin Fact Knowledge Layer.
Provides REST endpoints and serves the modern interactive web dashboard.
"""

import os
import shutil
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.schema import (
    Fact, FactRelationship, DocumentMetadata, KnowledgeLayerStats,
    FourCasesResponse, RelationshipType
)
from app.storage.database import DatabaseManager
from app.services.knowledge_layer import KnowledgeLayerService
from app.core.llm import llm_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Fact Knowledge Layer for grounded fact extraction, cross-document reconciliation, and epistemic reasoning."
)

# Enable CORS for local experimentation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mounting
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup():
    """Ensure starter PDFs exist and database is initialized."""
    # If no documents exist yet in DB, load the starter dataset automatically
    docs = DatabaseManager.get_all_documents()
    if not docs:
        print("[Startup] Initializing knowledge layer with starter dataset...")
        try:
            KnowledgeLayerService.load_starter_dataset()
        except Exception as e:
            print(f"[Startup] Error loading starter dataset: {e}")


@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    """Serve the main web dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Fact Knowledge Layer UI</h1><p>Static index.html not found.</p>")


@app.get("/api/stats", response_model=KnowledgeLayerStats)
def get_stats():
    """Retrieve summary metrics and counters."""
    return KnowledgeLayerService.get_stats()


@app.get("/api/documents", response_model=List[DocumentMetadata])
def list_documents():
    """List all ingested documents in the Knowledge Layer."""
    return DatabaseManager.get_all_documents()


@app.get("/api/facts", response_model=List[Fact])
def list_facts(
    document_id: Optional[str] = Query(None, description="Filter by Document ID"),
    entity: Optional[str] = Query(None, description="Filter by Entity"),
    search: Optional[str] = Query(None, description="Search query across attribute, value, quote")
):
    """Retrieve facts with filtering and search capabilities."""
    if document_id:
        facts = DatabaseManager.get_facts_by_document(document_id)
    else:
        facts = DatabaseManager.get_all_facts()

    if entity:
        facts = [f for f in facts if entity.lower() in f.entity.lower()]

    if search:
        s_lower = search.lower()
        facts = [
            f for f in facts
            if s_lower in f.attribute.lower()
            or s_lower in f.value.lower()
            or s_lower in f.exact_quote.lower()
            or s_lower in f.entity.lower()
        ]

    return facts


@app.get("/api/relationships", response_model=List[FactRelationship])
def list_relationships(
    type: Optional[str] = Query(None, description="Filter by relationship: all, corroborating, contradicting, reconciled")
):
    """Retrieve cross-document relationships with optional classification filter."""
    rels = DatabaseManager.get_all_relationships()
    if type and type.lower() != "all":
        t_upper = type.upper()
        rels = [r for r in rels if r.relationship_type.value == t_upper]
    return rels


@app.get("/api/four-cases", response_model=FourCasesResponse)
def get_four_cases():
    """Retrieve the four required evaluation case studies with evidence and reasoning."""
    return KnowledgeLayerService.get_four_cases_payload()


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Incrementally upload and ingest any new PDF into the knowledge layer.
    Extracts facts, indexes them, and runs cross-document reconciliation against existing facts.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    upload_path = settings.UPLOADS_DIR / file.filename
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc_meta = KnowledgeLayerService.ingest_pdf(str(upload_path), file.filename)
        new_facts = DatabaseManager.get_facts_by_document(doc_meta.id)
        return {
            "status": "success",
            "document": doc_meta,
            "facts_extracted": len(new_facts),
            "stats": KnowledgeLayerService.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.post("/api/load-starter")
def load_starter():
    """One-click reload of the authentic starter dataset."""
    result = KnowledgeLayerService.load_starter_dataset()
    return result


@app.post("/api/reset")
def reset_database():
    """Clear all indexed documents, facts, and relationships."""
    DatabaseManager.clear_all()
    return {"status": "success", "message": "Knowledge layer database cleared."}


@app.get("/api/config")
def get_configuration():
    """Check configuration and active LLM provider."""
    return {
        "provider": llm_client.provider,
        "gemini_configured": bool(llm_client.gemini_key),
        "groq_configured": bool(llm_client.groq_key),
        "openai_configured": bool(llm_client.openai_key),
        "model": llm_client.gemini_model
    }


@app.post("/api/settings")
def update_settings(
    provider: str = Form(...),
    api_key: Optional[str] = Form(None),
    model: Optional[str] = Form(None)
):
    """Update runtime LLM provider and API key."""
    llm_client.provider = provider.lower()
    if api_key:
        if provider.lower() == "gemini":
            llm_client.gemini_key = api_key
        elif provider.lower() == "groq":
            llm_client.groq_key = api_key
        elif provider.lower() == "openai":
            llm_client.openai_key = api_key
    if model:
        llm_client.gemini_model = model
    llm_client._init_client()
    return {"status": "success", "provider": llm_client.provider, "model": llm_client.gemini_model}

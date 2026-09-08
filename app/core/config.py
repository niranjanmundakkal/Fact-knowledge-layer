"""
Application configuration and environment settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env if present in workspace
load_dotenv(BASE_DIR / ".env")

# Also check parent DataOpsGPT .env as fallback if keys not in local .env
if not os.getenv("GEMINI_API_KEY") and not os.getenv("GROQ_API_KEY"):
    parent_env = BASE_DIR.parent / "DataOpsGPT" / "backend" / ".env"
    if parent_env.exists():
        load_dotenv(parent_env)

DATA_DIR = BASE_DIR / "data"
STARTER_PDFS_DIR = DATA_DIR / "starter_pdfs"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "knowledge_layer.sqlite"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STARTER_PDFS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "Superjoin Fact Knowledge Layer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    DEFAULT_LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq" if os.getenv("GROQ_API_KEY") else ("gemini" if os.getenv("GEMINI_API_KEY") else "offline"))
    
    DATA_DIR: Path = DATA_DIR
    STARTER_PDFS_DIR: Path = STARTER_PDFS_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    DB_PATH: Path = DB_PATH

settings = Settings()

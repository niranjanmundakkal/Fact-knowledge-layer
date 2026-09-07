import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.storage.database import init_db

def main():
    print("=" * 70)
    print("🚀 Starting Superjoin Fact Knowledge Layer System")
    print("=" * 70)

    # 1. Initialize SQLite database
    print("[1/3] Initializing persistent knowledge layer database...")
    init_db()

    # 2. Check and generate starter PDFs if needed
    starter_pdf = settings.STARTER_PDFS_DIR / "Delhivery_IPO_Prospectus_2022.pdf"
    if not starter_pdf.exists():
        print("[2/3] Generating starter PDF dataset...")
        import data.starter_pdfs.generate_starter_pdfs as gen_script
        gen_script.create_prospectus_pdf()
        gen_script.create_earnings_presentation_pdf()
        gen_script.create_annual_report_pdf()
        gen_script.create_economic_survey_pdf()
    else:
        print("[2/3] Starter PDF dataset verified.")

    # 3. Launch Uvicorn server
    print("[3/3] Launching FastAPI Web Server on http://127.0.0.1:8000 ...")
    print("\nAvailable Interfaces:")
    print("  • Web Dashboard:  http://127.0.0.1:8000")
    print("  • REST API Docs:  http://127.0.0.1:8000/docs")
    print("  • ReDoc Specs:    http://127.0.0.1:8000/redoc\n")
    print("Press Ctrl+C to stop the server.")

    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()

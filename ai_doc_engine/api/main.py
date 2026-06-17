from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.github_service import GitHubService
from engine.change_detector import ChangeDetector
from engine.staleness_classifier import StalenessClassifier

# We lazily initialize these to prevent loading two copies of PyTorch into memory 
# at startup (one for Streamlit, one for FastAPI) to stay under the 512MB Render limit.
db = None
llm = None
generator = None

app = FastAPI(title="AI Doc Engine API")
git_service = GitHubService()

UPDATES_FILE = "pending_updates.json"

def process_webhook_commit():
    global db, llm, generator
    if db is None:
        from engine.rag_store import DocVectorStore
        from engine.llm_service import LLMService
        from engine.doc_generator import DocGenerator
        db = DocVectorStore()
        llm_service = LLMService()
        generator = DocGenerator(llm_service=llm_service, db_store=db)
    else:
        llm_service = llm

    print("🔍 BACKGROUND TASK STARTED: Fetching latest commit...", flush=True)
    changes = git_service.get_latest_commit_diffs()
    print(f"📦 Found {len(changes)} changed files in the latest commit.", flush=True)
    
    if os.path.exists(UPDATES_FILE):
        with open(UPDATES_FILE, "r") as f:
            try:
                pending_updates = json.load(f)
            except json.JSONDecodeError:
                pending_updates = []
    else:
        pending_updates = []

    for change in changes:
        # We now use the dedicated ChangeDetector instead of messy inline logic
        detector = ChangeDetector(git_service, db)
        classifier = StalenessClassifier(llm_service)
        
        changed_units = detector.detect_changed_units(changes)
        
        for unit in changed_units:
            flag = classifier.classify(unit)
            
            if flag.draft_markdown:
                pending_updates.append({
                    "filename": flag.file_path,
                    "unit_name": flag.unit_name,
                    "severity": flag.severity,
                    "old_doc": unit.old_doc,
                    "new_doc_draft": flag.draft_markdown
                })
                print(f"✅ Added {flag.unit_name} to UI Review Queue.", flush=True)
                
        # Break early because the ChangeDetector handles the entire diff list at once
        break
    
    with open(UPDATES_FILE, "w") as f:
        json.dump(pending_updates, f)
        
    print(f"🏁 Background task complete. Saved {len(pending_updates)} flags total.", flush=True)

@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    print("🔔 WEBHOOK RECEIVED from GitHub!", flush=True)
    if "commits" in payload:
        print("✅ Push event detected. Triggering AI analysis...", flush=True)
        background_tasks.add_task(process_webhook_commit)
    else:
        print("ℹ️ Webhook received, but it wasn't a code push (commits array missing).", flush=True)
    return {"status": "Webhook received"}

from pydantic import BaseModel
class SearchQuery(BaseModel):
    query: str
    n_results: int = 3

class UpsertDoc(BaseModel):
    doc_id: str
    text: str
    metadata: dict

@app.post("/api/search")
async def api_search(query: SearchQuery):
    global db
    if db is None:
        from engine.rag_store import DocVectorStore
        db = DocVectorStore()
    return {"result": db.search(query.query, query.n_results)}

@app.post("/api/search_citations")
async def api_search_citations(query: SearchQuery):
    global db
    if db is None:
        from engine.rag_store import DocVectorStore
        db = DocVectorStore()
    docs, metas = db.search_with_citations(query.query, query.n_results)
    return {"docs": docs, "metas": metas}

@app.post("/api/upsert")
async def api_upsert(doc: UpsertDoc):
    global db
    if db is None:
        from engine.rag_store import DocVectorStore
        db = DocVectorStore()
    db.upsert_doc(doc.doc_id, doc.text, doc.metadata)
    return {"status": "success"}

@app.post("/api/ingest_repo")
async def api_ingest_repo(background_tasks: BackgroundTasks):
    def run_full_ingestion():
        global db, llm, generator
        if db is None:
            from engine.rag_store import DocVectorStore
            from engine.llm_service import LLMService
            from engine.doc_generator import DocGenerator
            db = DocVectorStore()
            llm_service = LLMService()
            generator = DocGenerator(llm_service=llm_service, db_store=db)
        print("🚀 Starting Full Manual Ingestion...", flush=True)
        generator.generate_for_repo(git_service)
        print("✅ Full Ingestion Complete!", flush=True)
        
    background_tasks.add_task(run_full_ingestion)
    return {"status": "started"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
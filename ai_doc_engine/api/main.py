from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.github_service import GitHubService
from engine.llm_service import LLMService
from engine.rag_store import DocVectorStore
from engine.change_detector import ChangeDetector
from engine.staleness_classifier import StalenessClassifier

app = FastAPI(title="AI Doc Engine API")
git_service = GitHubService()
llm_service = LLMService()
db = DocVectorStore()

UPDATES_FILE = "/app/chroma_db/pending_updates.json"

def process_webhook_commit():
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
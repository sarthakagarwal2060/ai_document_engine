import os
from engine.ast_parser import CodeParser
from engine.models import ParsedCodeUnit
from concurrent.futures import ThreadPoolExecutor, as_completed

class DocGenerator:
    def __init__(self, llm_service, db_store):
        self.llm = llm_service
        self.db = db_store

    def _process_single_unit(self, unit, path):
        print(f"  🧠 [Thread] Generating docs for {unit.unit_type}: {unit.name}...", flush=True)
        try:
            doc = self.llm.generate_documentation(unit)
            doc_id = f"{path}::{unit.name}"
            self.db.upsert_doc(doc_id=doc_id, text=doc, metadata={
                "file_path": path,
                "unit_type": unit.unit_type,
                "name": unit.name
            })
            return True
        except Exception as e:
            print(f"❌ Error generating doc for {unit.name}: {str(e)}", flush=True)
            return False
            
    def _process_entire_file(self, content, path):
        print(f"⚠️ [Thread] Generating docs for entire file: {path}", flush=True)
        try:
            doc = self.llm.generate_documentation(content)
            self.db.upsert_doc(doc_id=path, text=doc, metadata={"file_path": path, "unit_type": "file"})
            return True
        except Exception as e:
            print(f"❌ Error generating doc for {path}: {str(e)}", flush=True)
            return False

    def generate_for_repo(self, git_service, ref="main"):
        print("🚀 Starting Full Repository Documentation Generation...", flush=True)
        files = git_service.fetch_all_code_files(ref=ref)
        
        # Phase 1: Parse everything sequentially into a flat list of tasks
        tasks = []
        for file in files:
            path = file['path']
            print(f"📄 Parsing file: {path}", flush=True)
            
            content = git_service.get_file_content(path, ref=ref)
            
            try:
                units = CodeParser.parse_file(path, content)
                if not units:
                    tasks.append(('file', content, path))
                else:
                    for unit in units:
                        tasks.append(('unit', unit, path))
            except Exception as e:
                print(f"❌ Failed to parse {path}: {e}")
                
        print(f"⚡ Queued {len(tasks)} code units. Firing parallel LLM requests...", flush=True)
        
        # Phase 2: Execute LLM calls concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for task_type, payload, path in tasks:
                if task_type == 'file':
                    futures.append(executor.submit(self._process_entire_file, payload, path))
                else:
                    futures.append(executor.submit(self._process_single_unit, payload, path))
                    
            for future in as_completed(futures):
                future.result() # Wait for all threads to finish
                
        print("✅ Repository Documentation Complete!", flush=True)

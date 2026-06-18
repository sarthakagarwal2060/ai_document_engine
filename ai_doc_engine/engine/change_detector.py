from typing import List
from engine.models import ChangedUnit
from engine.ast_parser import CodeParser
from engine.rag_store import DocVectorStore
from engine.github_service import GitHubService

class ChangeDetector:
    def __init__(self, github_service: GitHubService, db_store: DocVectorStore):
        self.git = github_service
        self.db = db_store

    def detect_changed_units(self, diffs: List[dict]) -> List[ChangedUnit]:
        """
        Takes raw Git diffs, parses the new file contents, and figures out exactly
        which Code Units (functions/classes) were touched by the commit.
        """
        changed_units = []
        
        for diff in diffs:
            filename = diff.get("filename")
            patch = diff.get("patch")
            
            if not patch or not filename:
                continue
                
            # Get the new content of the file
            content = self.git.get_file_content(filename)
            if not content:
                continue
                
            # Parse the new file into its granular units
            units = CodeParser.parse_file(filename, content)
            
            if not units:
                # Fallback: Treat the whole file as one giant unit
                old_doc = self._get_old_doc(filename)
                changed_units.append(ChangedUnit(
                    file_path=filename,
                    unit_name=filename,
                    patch=patch,
                    old_doc=old_doc
                ))
                continue
                
            # See which specific units are actually affected by the patch
            for unit in units:
                # Heuristic: If the unit's name appears in the Git patch, it was modified
                if unit.name in patch:
                    doc_id = f"{filename}::{unit.name}"
                    old_doc = self._get_old_doc(doc_id)
                    
                    changed_units.append(ChangedUnit(
                        file_path=filename,
                        unit_name=unit.name,
                        patch=patch,
                        old_doc=old_doc
                    ))
                    
        return changed_units
        
    def _get_old_doc(self, doc_id: str) -> str:
        """Retrieves existing documentation from Pinecone safely."""
        return self.db.get_doc(doc_id)

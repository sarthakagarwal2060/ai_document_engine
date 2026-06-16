from engine.models import ChangedUnit, StalenessFlag
from engine.llm_service import LLMService

class StalenessClassifier:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def classify(self, changed_unit: ChangedUnit) -> StalenessFlag:
        """
        Uses the LLM to determine if the documentation needs to be updated based
        on the git patch. If it's stale, it extracts the AI's draft.
        """
        if not changed_unit.old_doc:
            # If there's no old doc, this is a completely new function/class! 
            # We flag it as BROKEN so the team is forced to review the new AI draft.
            print(f"🌟 New unit detected ({changed_unit.unit_name}). Generating initial doc draft...", flush=True)
            draft = self.llm.generate_documentation(changed_unit.patch)
            return StalenessFlag(
                file_path=changed_unit.file_path,
                unit_name=changed_unit.unit_name,
                severity="BROKEN",
                draft_markdown=draft
            )

        print(f"🧠 Classifying staleness for {changed_unit.unit_name}...", flush=True)
        raw_analysis = self.llm.detect_staleness_and_draft(changed_unit.old_doc, changed_unit.patch)
        
        severity = "REVIEW_RECOMMENDED"
        updated_doc = raw_analysis
        
        # Parse the structured output from the LLM prompt
        if "SEVERITY:" in raw_analysis and "UPDATED_DOC:" in raw_analysis:
            parts = raw_analysis.split("UPDATED_DOC:")
            severity = parts[0].replace("SEVERITY:", "").strip()
            updated_doc = parts[1].strip()
            
        print(f"🤖 AI Verdict for {changed_unit.unit_name}: {severity}", flush=True)
        
        # Only return the draft if the AI determined it wasn't SAFE
        is_stale = "SAFE" not in severity.upper()
        
        return StalenessFlag(
            file_path=changed_unit.file_path,
            unit_name=changed_unit.unit_name,
            severity=severity,
            draft_markdown=updated_doc if is_stale else None
        )

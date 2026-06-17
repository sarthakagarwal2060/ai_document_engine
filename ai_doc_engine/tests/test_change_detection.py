import unittest
from unittest.mock import MagicMock
from engine.change_detector import ChangeDetector
from engine.staleness_classifier import StalenessClassifier
from engine.github_service import GitHubService
from engine.rag_store import DocVectorStore
from engine.models import ChangedUnit

class TestChangeDetectionPipeline(unittest.TestCase):
    def setUp(self):
        # Mock GitHub
        self.mock_git = MagicMock(spec=GitHubService)
        self.mock_git.get_file_content.return_value = "def test_func():\n    pass"
        
        # Mock Database
        self.mock_db = MagicMock(spec=DocVectorStore)
        self.mock_db.collection.get.return_value = {'documents': ['Old Doc']}
        
        # Mock LLM (for Staleness Classifier)
        self.mock_llm = MagicMock()
        self.mock_llm.detect_staleness_and_draft.return_value = "SEVERITY: BROKEN\nUPDATED_DOC: # New Doc"
        
    def test_change_detector_identifies_unit(self):
        detector = ChangeDetector(self.mock_git, self.mock_db)
        
        mock_diffs = [{
            "filename": "test.py",
            "patch": "@@ -1,2 +1,2 @@\n-def test_func():\n+def test_func(x):"
        }]
        
        changed_units = detector.detect_changed_units(mock_diffs)
        
        # It should correctly identify that 'test_func' was changed
        self.assertEqual(len(changed_units), 1)
        self.assertEqual(changed_units[0].unit_name, "test_func")
        self.assertEqual(changed_units[0].file_path, "test.py")

    def test_staleness_classifier_formats_flag(self):
        classifier = StalenessClassifier(self.mock_llm)
        unit = ChangedUnit(file_path="test.py", unit_name="test_func", patch="patch", old_doc="old")
        
        flag = classifier.classify(unit)
        
        # It should correctly parse the structured LLM output
        self.assertEqual(flag.severity, "BROKEN")
        self.assertEqual(flag.draft_markdown, "# New Doc")

if __name__ == '__main__':
    unittest.main()

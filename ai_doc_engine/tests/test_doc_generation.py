import unittest
from unittest.mock import MagicMock
from engine.doc_generator import DocGenerator
from engine.llm_service import LLMService
from engine.rag_store import DocVectorStore
from engine.models import ParsedCodeUnit

class TestDocGenerator(unittest.TestCase):
    def setUp(self):
        # Mock the LLM service to avoid real API calls
        self.mock_llm = MagicMock(spec=LLMService)
        self.mock_llm.generate_documentation.return_value = "# Mocked Documentation"
        
        # Mock the Database
        self.mock_db = MagicMock(spec=DocVectorStore)
        
        self.generator = DocGenerator(self.mock_llm, self.mock_db)

    def test_generate_for_file_python(self):
        # A simple Python snippet to parse
        mock_code = """
def test_func(x: int) -> int:
    return x * 2
"""
        
        self.generator.generate_for_file("test.py", mock_code)
        
        # Verify the LLM was called exactly once (for the test_func)
        self.mock_llm.generate_documentation.assert_called_once()
        
        # Extract the argument passed to the LLM
        args, _ = self.mock_llm.generate_documentation.call_args
        passed_unit = args[0]
        
        # Verify the parser successfully created a ParsedCodeUnit
        self.assertIsInstance(passed_unit, ParsedCodeUnit)
        self.assertEqual(passed_unit.name, "test_func")
        
        # Verify the database upsert was called with the correct ID
        self.mock_db.upsert_doc.assert_called_once()
        db_args, db_kwargs = self.mock_db.upsert_doc.call_args
        self.assertEqual(db_kwargs['doc_id'], "test.py::test_func")
        self.assertEqual(db_kwargs['text'], "# Mocked Documentation")

if __name__ == '__main__':
    unittest.main()

from .parsers.python_parser import PythonParser
from .models import ParsedCodeUnit
from typing import List

class CodeParser:
    @staticmethod
    def parse_file(file_path: str, code_string: str) -> List[ParsedCodeUnit]:
        """Routes to the correct language parser based on file extension."""
        if file_path.endswith('.py'):
            return PythonParser.parse(code_string, file_path)
            
        # Java and JS fallback parsers will be added here
        
        return []
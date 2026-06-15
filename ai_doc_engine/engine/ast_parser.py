from .parsers.python_parser import PythonParser
from .parsers.java_parser import JavaParser
from .parsers.js_parser import JSParser
from .models import ParsedCodeUnit
from typing import List

class CodeParser:
    @staticmethod
    def parse_file(file_path: str, code_string: str) -> List[ParsedCodeUnit]:
        """Routes to the correct language parser based on file extension."""
        if file_path.endswith('.py'):
            return PythonParser.parse(code_string, file_path)
        elif file_path.endswith('.java'):
            return JavaParser.parse(code_string, file_path)
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            return JSParser.parse(code_string, file_path)
            
        return []
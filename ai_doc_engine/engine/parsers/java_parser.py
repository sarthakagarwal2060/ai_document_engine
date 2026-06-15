import re
from typing import List
from ..models import ParsedCodeUnit

class JavaParser:
    @staticmethod
    def parse(code_string: str, file_path: str) -> List[ParsedCodeUnit]:
        """Parses Java source code using regex to extract classes and methods with Javadocs."""
        elements = []
        
        # Regex for Javadoc
        doc_pattern = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)
        
        # Simplified Regex for classes and methods
        class_pattern = re.compile(r'(?:public|private|protected)?\s*(?:static|final|abstract)?\s*class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{')
        # Matches e.g. public void myMethod(String arg) throws Exception {
        method_pattern = re.compile(r'(?:public|private|protected)?\s*(?:static|final|abstract)?\s*([\w<>\[\]]+)\s+(\w+)\s*\((.*?)\)\s*(?:throws\s+[\w\s,]+)?\s*\{')
        
        # Extract classes
        for match in class_pattern.finditer(code_string):
            class_name = match.group(1)
            preceding_text = code_string[:match.start()]
            docs = doc_pattern.findall(preceding_text)
            docstring = docs[-1].strip() if docs else None
            
            line_num = code_string[:match.start()].count('\n') + 1
            
            elements.append(ParsedCodeUnit(
                unit_type="class",
                name=class_name,
                file_path=file_path,
                signature=match.group(0).strip()[:-1].strip(), # remove trailing {
                docstring=docstring,
                return_type=None,
                parameters=[],
                raw_code=match.group(0).strip()[:-1].strip(), # Store signature as raw code fallback
                line_start=line_num,
                line_end=line_num
            ))
            
        # Extract methods
        for match in method_pattern.finditer(code_string):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)
            
            # Skip common keywords that might match the method pattern
            if method_name in ('if', 'for', 'while', 'switch', 'catch'):
                continue
                
            preceding_text = code_string[:match.start()]
            docs = doc_pattern.findall(preceding_text)
            docstring = docs[-1].strip() if docs else None
            
            line_num = code_string[:match.start()].count('\n') + 1
            
            # Parse parameters
            params = []
            if params_str.strip():
                for param in params_str.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        p_type = " ".join(parts[:-1])
                        p_name = parts[-1]
                        params.append({"name": p_name, "type": p_type, "default": None})
            
            elements.append(ParsedCodeUnit(
                unit_type="function",
                name=method_name,
                file_path=file_path,
                signature=match.group(0).strip()[:-1].strip(),
                docstring=docstring,
                return_type=return_type,
                parameters=params,
                raw_code=match.group(0).strip()[:-1].strip(),
                line_start=line_num,
                line_end=line_num
            ))
            
        return elements

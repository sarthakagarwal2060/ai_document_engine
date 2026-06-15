import re
from typing import List
from ..models import ParsedCodeUnit

class JSParser:
    @staticmethod
    def parse(code_string: str, file_path: str) -> List[ParsedCodeUnit]:
        """Parses JavaScript/TypeScript source code using regex to extract classes and functions."""
        elements = []
        
        # Regex for JSDoc
        doc_pattern = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)
        
        # Simplified Regex for classes, functions, and arrow functions
        class_pattern = re.compile(r'(?:export\s+)?(?:default\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*\{')
        function_pattern = re.compile(r'(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)\s*(?::\s*([\w<>\[\]|&]+))?\s*\{')
        arrow_pattern = re.compile(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\((.*?)\)\s*(?::\s*([\w<>\[\]|&]+))?\s*=>\s*\{')
        
        def extract(pattern, unit_type):
            for match in pattern.finditer(code_string):
                name = match.group(1)
                
                preceding_text = code_string[:match.start()]
                docs = doc_pattern.findall(preceding_text)
                docstring = docs[-1].strip() if docs else None
                
                line_num = code_string[:match.start()].count('\n') + 1
                
                if unit_type == "class":
                    elements.append(ParsedCodeUnit(
                        unit_type="class",
                        name=name,
                        file_path=file_path,
                        signature=match.group(0).strip()[:-1].strip(),
                        docstring=docstring,
                        return_type=None,
                        parameters=[],
                        raw_code=match.group(0).strip()[:-1].strip(),
                        line_start=line_num,
                        line_end=line_num
                    ))
                else:
                    params_str = match.group(2)
                    return_type = match.group(3) if len(match.groups()) >= 3 else None
                    
                    # Parse parameters (very basic TS typing split)
                    params = []
                    if params_str.strip():
                        for param in params_str.split(','):
                            parts = param.strip().split(':')
                            p_name = parts[0].strip()
                            p_type = parts[1].strip() if len(parts) > 1 else None
                            params.append({"name": p_name, "type": p_type, "default": None})
                            
                    # Clean up signature
                    sig = match.group(0).strip()[:-1].strip()
                    if sig.endswith('=>'):
                        sig = sig[:-2].strip()
                        
                    elements.append(ParsedCodeUnit(
                        unit_type="function",
                        name=name,
                        file_path=file_path,
                        signature=sig,
                        docstring=docstring,
                        return_type=return_type,
                        parameters=params,
                        raw_code=sig,
                        line_start=line_num,
                        line_end=line_num
                    ))
                    
        extract(class_pattern, "class")
        extract(function_pattern, "function")
        extract(arrow_pattern, "function")
            
        return elements

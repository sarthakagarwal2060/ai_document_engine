import ast
from typing import List, Any, Dict
from ..models import ParsedCodeUnit

class PythonParser:
    @staticmethod
    def parse(code_string: str, file_path: str) -> List[ParsedCodeUnit]:
        """Parses Python source code and extracts functions, classes, and module docstrings."""
        try:
            tree = ast.parse(code_string)
        except SyntaxError:
            return []
            
        elements = []
        
        # 1. Module level docstring
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            elements.append(ParsedCodeUnit(
                unit_type="module",
                name="<module>",
                file_path=file_path,
                signature="",
                docstring=module_docstring,
                return_type=None,
                parameters=[],
                raw_code=code_string,
                line_start=1,
                line_end=len(code_string.splitlines())
            ))
            
        # 2. Walk AST to find functions and classes
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                
                # Extract parameters
                params = []
                # Map defaults (defaults align to the end of the args list)
                defaults_offset = len(node.args.args) - len(node.args.defaults)
                for i, arg in enumerate(node.args.args):
                    param_type = ast.unparse(arg.annotation) if arg.annotation else None
                    default_val = None
                    if i >= defaults_offset:
                        default_node = node.args.defaults[i - defaults_offset]
                        default_val = ast.unparse(default_node)
                        
                    params.append({"name": arg.arg, "type": param_type, "default": default_val})
                    
                # Extract return type
                return_type = ast.unparse(node.returns) if node.returns else None
                
                # Build signature string
                args_str_parts = []
                for p in params:
                    part = p['name']
                    if p['type']:
                        part += f": {p['type']}"
                    if p['default']:
                        part += f" = {p['default']}"
                    args_str_parts.append(part)
                    
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                sig = f"{prefix} {node.name}({', '.join(args_str_parts)})"
                if return_type:
                    sig += f" -> {return_type}"
                    
                elements.append(ParsedCodeUnit(
                    unit_type="function",
                    name=node.name,
                    file_path=file_path,
                    signature=sig,
                    docstring=docstring,
                    return_type=return_type,
                    parameters=params,
                    raw_code=ast.unparse(node),
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno
                ))
                
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                
                # Extract base classes
                bases = [ast.unparse(b) for b in node.bases]
                bases_str = f"({', '.join(bases)})" if bases else ""
                
                elements.append(ParsedCodeUnit(
                    unit_type="class",
                    name=node.name,
                    file_path=file_path,
                    signature=f"class {node.name}{bases_str}",
                    docstring=docstring,
                    return_type=None,
                    parameters=[],
                    raw_code=ast.unparse(node),
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno
                ))
                
        return elements

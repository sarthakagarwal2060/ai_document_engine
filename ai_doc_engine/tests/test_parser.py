import os
import sys

# Ensure engine modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.ast_parser import CodeParser

def test_python_parser():
    code = """
def my_function(a: int, b: str = "test") -> bool:
    '''This is a docstring'''
    return True
    
class MyClass:
    '''Class docstring'''
    pass
"""
    elements = CodeParser.parse_file("test.py", code)
    
    assert len(elements) == 2, f"Expected 2 elements, got {len(elements)}"
    
    func = elements[0]
    assert func.unit_type == "function"
    assert func.name == "my_function"
    assert func.docstring == "This is a docstring"
    assert func.return_type == "bool"
    assert len(func.parameters) == 2
    assert func.parameters[0]["name"] == "a"
    assert func.parameters[0]["type"] == "int"
    assert func.parameters[1]["name"] == "b"
    assert func.parameters[1]["default"] == "'test'"
    
    cls = elements[1]
    assert cls.unit_type == "class"
    assert cls.name == "MyClass"
    assert cls.docstring == "Class docstring"


def test_java_parser():
    code = """
/** Class docstring */
public class JavaTest {
    /** Method docstring */
    public void myMethod(String arg1, int arg2) {
    }
}
"""
    elements = CodeParser.parse_file("Test.java", code)
    assert len(elements) == 2
    
    cls = elements[0]
    assert cls.unit_type == "class"
    assert cls.name == "JavaTest"
    assert cls.docstring == "Class docstring"
    
    method = elements[1]
    assert method.unit_type == "function"
    assert method.name == "myMethod"
    assert method.docstring == "Method docstring"
    assert method.return_type == "void"
    assert len(method.parameters) == 2
    assert method.parameters[0]["name"] == "arg1"
    assert method.parameters[0]["type"] == "String"
    assert method.parameters[1]["name"] == "arg2"
    assert method.parameters[1]["type"] == "int"


def test_js_parser():
    code = """
/** Class docstring */
export class JsClass {
}

/** Function docstring */
async function jsFunc(a: string, b: number): Promise<void> {
}

/** Arrow docstring */
export const arrowFunc = async (x: string) => {
}
"""
    elements = CodeParser.parse_file("test.ts", code)
    assert len(elements) == 3
    
    cls = elements[0]
    assert cls.unit_type == "class"
    assert cls.name == "JsClass"
    assert cls.docstring == "Class docstring"
    
    func = elements[1]
    assert func.unit_type == "function"
    assert func.name == "jsFunc"
    assert func.docstring == "Function docstring"
    assert func.return_type == "Promise<void>"
    assert len(func.parameters) == 2
    assert func.parameters[0]["name"] == "a"
    assert func.parameters[0]["type"] == "string"
    
    arrow = elements[2]
    assert arrow.unit_type == "function"
    assert arrow.name == "arrowFunc"
    assert arrow.docstring == "Arrow docstring"
    assert arrow.return_type is None
    assert len(arrow.parameters) == 1
    assert arrow.parameters[0]["name"] == "x"
    assert arrow.parameters[0]["type"] == "string"

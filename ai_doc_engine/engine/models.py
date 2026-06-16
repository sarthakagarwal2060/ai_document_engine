from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ParsedCodeUnit:
    """
    Shared model representing a parsed piece of code (function, class, or module).
    This serves as the core interface between the ingestion/parsing engine and the documentation generation engine.
    """
    unit_type: str          # "function", "class", or "module"
    name: str               # The name of the function or class
    file_path: str          # The source file path
    signature: str          # The complete signature (e.g., "def foo(a: int) -> bool")
    docstring: Optional[str] # The original docstring, if any
    return_type: Optional[str] # The return type hint
    parameters: List[Dict[str, Any]]  # List of param dicts, e.g. [{"name": "x", "type": "int", "default": None}]
    raw_code: str           # The raw source code of this unit
    line_start: int         # Starting line number
    line_end: int           # Ending line number

@dataclass
class ChangedUnit:
    """Represents a code unit that was modified in a commit."""
    file_path: str
    unit_name: str
    patch: str  # The raw git diff patch
    old_doc: Optional[str] = None  # The existing documentation from the vector DB

@dataclass
class StalenessFlag:
    """Represents the AI's verdict on whether a ChangedUnit needs new documentation."""
    file_path: str
    unit_name: str
    severity: str  # e.g., SAFE, REVIEW_RECOMMENDED, POTENTIALLY_OUTDATED, BROKEN
    draft_markdown: Optional[str] = None  # The AI's suggested new documentation


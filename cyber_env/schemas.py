from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Sub-components of the Codebase State ---

class FileInfo(BaseModel):
    path: str = Field(description="Relative path of the file")
    content: str = Field(description="Current content of the file")

class ScanResult(BaseModel):
    tool: str = Field(description="SAST tool name (e.g., 'bandit', 'semgrep')")
    output: str = Field(description="Raw output from the security scan")
    passed: bool = Field(description="True if no vulnerabilities found")

class TestResult(BaseModel):
    output: str = Field(description="Raw output from unit tests")
    passed: bool = Field(description="True if all tests pass")

# --- The Main State Model ---

class CodebaseState(BaseModel):
    """The complete observable state of the simulated codebase."""
    file_tree: List[str] = Field(description="List of file paths in the codebase")
    current_files: List[FileInfo] = Field(description="Contents of files that have been read")
    security_scan: Optional[ScanResult] = Field(None, description="Result of the last security scan")
    unit_tests: Optional[TestResult] = Field(None, description="Result of the last unit test run")

# --- Action Models ---

from typing import Literal, Union

class ReadFileAction(BaseModel):
    action_type: Literal["read_file"] = "read_file"
    filepath: str = Field(description="Relative path of the file to read")

class SearchReplaceAction(BaseModel):
    action_type: Literal["search_and_replace"] = "search_and_replace"
    filepath: str = Field(description="Relative path of the file to edit")
    old_snippet: str = Field(description="Exact string to replace (must match exactly)")
    new_snippet: str = Field(description="New string to replace with")

class RunSecurityScanAction(BaseModel):
    action_type: Literal["run_security_scan"] = "run_security_scan"

class RunUnitTestsAction(BaseModel):
    action_type: Literal["run_unit_tests"] = "run_unit_tests"

# The unified Action type
AgentAction = Union[
    ReadFileAction,
    SearchReplaceAction,
    RunSecurityScanAction,
    RunUnitTestsAction
]
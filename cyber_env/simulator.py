import os
import subprocess
import tempfile
from .schemas import CodebaseState, FileInfo, ScanResult, TestResult

class SimulatedCodebase:
    def __init__(self):
        self.files = {}  # path -> content
        self.read_files = set()
        self.security_scan = None
        self.unit_tests = None
        self.temp_dir = tempfile.mkdtemp()

    def get_state(self) -> CodebaseState:
        current_files = [FileInfo(path=path, content=content) for path, content in self.files.items() if path in self.read_files]
        return CodebaseState(
            file_tree=list(self.files.keys()),
            current_files=current_files,
            security_scan=self.security_scan,
            unit_tests=self.unit_tests
        )

    def read_file(self, filepath: str) -> bool:
        if filepath in self.files:
            self.read_files.add(filepath)
            return True
        return False

    def search_replace(self, filepath: str, old_snippet: str, new_snippet: str) -> bool:
        if filepath in self.files:
            content = self.files[filepath]
            if old_snippet in content:
                self.files[filepath] = content.replace(old_snippet, new_snippet, 1)
                return True
        return False

    def run_security_scan(self):
        # Simulate Bandit for Python, or Semgrep
        # For simplicity, check for common issues
        output = ""
        passed = True
        for path, content in self.files.items():
            if "sk-" in content or "password" in content.lower():
                output += f"High: Hardcoded secret in {path}\n"
                passed = False
            if "subprocess.run" in content and "shell=True" in content:
                output += f"High: Command injection in {path}\n"
                passed = False
            if "strcpy" in content and ".cpp" in path:
                output += f"High: Unsafe strcpy in {path}\n"
                passed = False
        self.security_scan = ScanResult(tool="bandit", output=output, passed=passed)

    def run_unit_tests(self):
        # Simulate pytest
        output = ""
        passed = True
        # Simple checks
        for path, content in self.files.items():
            if "test_" in path:
                if "assert" in content:
                    output += f"test passed for {path}\n"
                else:
                    output += f"test failed for {path}\n"
                    passed = False
        self.unit_tests = TestResult(output=output, passed=passed)
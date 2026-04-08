from .simulator import SimulatedCodebase

# --- TASK 1: EASY (Python - The Leaked Secret) ---
def setup_task_1(codebase: SimulatedCodebase):
    codebase.files["app.py"] = """
import os

API_KEY = "sk-1234567890abcdef"  # Hardcoded secret
print("API Key:", API_KEY)
"""
    codebase.files["test_app.py"] = """
import os
os.environ['API_KEY'] = 'test_key'
def test_app():
    import app
    assert app.API_KEY == 'test_key'  # Should use env var
"""

def grade_task_1(codebase: SimulatedCodebase) -> float:
    score = 0.0
    if "app.py" in codebase.read_files:
        score += 0.2
    if codebase.security_scan and codebase.security_scan.passed:
        score += 0.3
    if codebase.unit_tests and codebase.unit_tests.passed:
        score += 0.5
    # Ensure score is strictly between 0 and 1 (exclusive)
    score = min(score, 0.99)  # Cap at 0.99, not 1.0
    score = max(score, 0.01)  # Floor at 0.01, not 0.0
    return score

# --- TASK 2: MEDIUM (Python - Command Injection) ---
def setup_task_2(codebase: SimulatedCodebase):
    codebase.files["utils.py"] = """
import subprocess

def run_command(user_input):
    subprocess.run(user_input, shell=True)  # Vulnerable
"""
    codebase.files["test_utils.py"] = """
def test_run_command():
    from utils import run_command
    # Test safe input
    run_command(["echo", "hello"])
"""

def grade_task_2(codebase: SimulatedCodebase) -> float:
    score = 0.0
    if "utils.py" in codebase.read_files:
        score += 0.2
    if codebase.security_scan and codebase.security_scan.passed:
        score += 0.3
    if codebase.unit_tests and codebase.unit_tests.passed:
        score += 0.5
    # Ensure score is strictly between 0 and 1 (exclusive)
    score = min(score, 0.99)  # Cap at 0.99, not 1.0
    score = max(score, 0.01)  # Floor at 0.01, not 0.0
    return score

# --- TASK 3: HARD (C++ - Memory Safety) ---
def setup_task_3(codebase: SimulatedCodebase):
    codebase.files["main.cpp"] = """
#include <cstring>

void copy_string(char* dest, const char* src) {
    strcpy(dest, src);  // Buffer overflow risk
}
"""
    codebase.files["test_main.cpp"] = """
// Assume compiled and tested
"""

def grade_task_3(codebase: SimulatedCodebase) -> float:
    score = 0.0
    if "main.cpp" in codebase.read_files:
        score += 0.2
    if codebase.security_scan and codebase.security_scan.passed:
        score += 0.3
    if codebase.unit_tests and codebase.unit_tests.passed:
        score += 0.5
    # Ensure score is strictly between 0 and 1 (exclusive)
    score = min(score, 0.99)  # Cap at 0.99, not 1.0
    score = max(score, 0.01)  # Floor at 0.01, not 0.0
    return score
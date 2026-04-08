from .simulator import SimulatedCodebase

# ============================================================================
# TASK 1: EASY - Multi-File Secret Management
# ============================================================================
# Real-world scenario: Finding and replacing hardcoded secrets across codebase
# Difficulty: Agent must search multiple files and understand secret types

def setup_task_1(codebase: SimulatedCodebase):
    """Setup Task 1: Multiple hardcoded secrets across files."""
    
    # File 1: Main application with API key
    codebase.files["app.py"] = """import os
from config import DB_USER, DB_PASS

API_KEY_OPENAI = "sk-1234567890abcdef"  # Hardcoded secret!
API_KEY_STRIPE = "sk_live_51234567890abcdef"  # Another hardcoded secret!

def initialize_app():
    # TODO: Use environment variables instead of hardcoding
    print(f"Connecting with keys: {API_KEY_OPENAI}")
    setup_database(DB_USER, DB_PASS)

if __name__ == "__main__":
    initialize_app()
"""

    # File 2: Configuration with DB credentials
    codebase.files["config.py"] = """# Database configuration
# TODO: Move sensitive data to .env file before production

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "username": "admin",
    "password": "prod_password_abc123",  # Hardcoded password!
    "database": "production_db"
}

DB_USER = DATABASE_CONFIG["username"]
DB_PASS = DATABASE_CONFIG["password"]
"""

    # File 3: Utility functions with another secret (red herring mix)
    codebase.files["utils.py"] = """import requests

# API credentials hardcoded
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnop"  # Hardcoded secret!
API_ENDPOINT = "https://api.github.com"

def fetch_repo_data(owner, repo):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",  # Using hardcoded token
        "Accept": "application/vnd.github.v3+json"
    }
    return requests.get(f"{API_ENDPOINT}/repos/{owner}/{repo}", headers=headers)

def safe_log_info(data):
    # This is OK - just logging, not a security issue (red herring check)
    print(f"Processing data from: {data}")
    return True
"""

    # File 4: Test file with proper environment usage (red herring)
    codebase.files["test_app.py"] = """import os
import pytest

# Correct way - using environment variables in tests
@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("API_KEY_OPENAI", "test_key_123")
    monkeypatch.setenv("API_KEY_STRIPE", "test_stripe_key")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASS", "test_pass")

def test_app_initialization(setup_env):
    from app import initialize_app
    # Should work with env vars, not hardcoded values
    initialize_app()

def test_config_from_env(setup_env):
    os.environ["DB_USER"] = "test_admin"
    os.environ["DB_PASS"] = "test_password"
    # Once fixed, config should read from these
"""

    # File 5: .env.example (red herring - not a real issue)
    codebase.files[".env.example"] = """# Environment variables - NEVER commit .env file with real secrets!
API_KEY_OPENAI=sk_test_xxxxxxxxxxxx
API_KEY_STRIPE=sk_test_xxxxxxxxxxxx
DB_USER=admin
DB_PASS=password_here
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
"""

def grade_task_1(codebase: SimulatedCodebase) -> float:
    """Grade Task 1: Check if all secrets are properly removed."""
    score = 0.0
    
    # 0.1: Read at least one file (discovery)
    if len(codebase.read_files) >= 1:
        score += 0.1
    
    # 0.2: All secret files have been read
    secret_files = {"app.py", "config.py", "utils.py"}
    if secret_files.issubset(codebase.read_files):
        score += 0.15
    
    # 0.3: Check if all secrets have been removed
    secrets_removed = 0
    potential_secrets = [
        ("app.py", "sk-"),
        ("app.py", "sk_live"),
        ("config.py", "prod_password"),
        ("utils.py", "ghp_"),
    ]
    
    for filepath, secret_pattern in potential_secrets:
        if filepath in codebase.files:
            if secret_pattern not in codebase.files[filepath]:
                secrets_removed += 1
    
    if secrets_removed >= 3:
        score += 0.25
    elif secrets_removed == 2:
        score += 0.12
    
    # 0.15: Security scan passes (no more hardcoded secrets detected)
    if codebase.security_scan and codebase.security_scan.passed:
        score += 0.15
    
    # 0.2: Tests pass (configuration works with env vars)
    if codebase.unit_tests and codebase.unit_tests.passed:
        score += 0.15
    
    # Ensure score is strictly between 0 and 1 (exclusive)
    score = min(score, 0.99)
    score = max(score, 0.01)
    return score


# ============================================================================
# TASK 2: MEDIUM - SQL Injection + NoSQL Injection
# ============================================================================
# Real-world scenario: Database queries vulnerable to injection attacks
# Difficulty: Agent must understand different database paradigms and safe practices

def setup_task_2(codebase: SimulatedCodebase):
    """Setup Task 2: SQL and NoSQL injection vulnerabilities."""
    
    # File 1: Flask app with SQL injection
    codebase.files["app.py"] = """from flask import Flask, request
import sqlite3

app = Flask(__name__)
db_connection = sqlite3.connect('users.db')

@app.route('/user')
def get_user():
    # TODO: Use parameterized queries before production!
    username = request.args.get('username')
    
    # VULNERABLE: SQL Injection!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor = db_connection.execute(query)
    return cursor.fetchall()

@app.route('/admin')
def admin_check():
    user_id = request.args.get('user_id')
    
    # VULNERABLE: Another SQL Injection!
    query = f"SELECT role FROM user_roles WHERE id = {user_id}"
    cursor = db_connection.execute(query)
    return cursor.fetchone()

if __name__ == '__main__':
    app.run(debug=False)
"""

    # File 2: MongoDB handler with NoSQL injection
    codebase.files["mongo_handler.py"] = """from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['secure_app']
users_collection = db['users']

def find_user_by_id(user_input):
    # TODO: Always validate and convert to ObjectId!
    # VULNERABLE: NoSQL Injection!
    try:
        query = {"_id": ObjectId(user_input)}
    except:
        # Attacker could exploit this with: {"_id": {"$ne": null}}
        query = user_input  # Direct injection!
    
    return users_collection.find_one(query)

def find_user_by_email(email_input):
    # VULNERABLE: NoSQL Injection through string concatenation!
    # {"email": email_input} where email_input = {"$regex": ".*password.*"}
    query = {"email": email_input}
    return users_collection.find_one(query)

def safe_logging_function(data):
    # This looks like it might be vulnerable but it's NOT (red herring)
    # Log data doesn't interact with database
    print(f"User accessed: {data}")
    return True
"""

    # File 3: Tests with security assertions
    codebase.files["test_security.py"] = """import pytest
from app import app, db_connection
from mongo_handler import find_user_by_id, find_user_by_email

class TestSQLInjectionPrevention:
    def test_username_with_sql_injection_payload(self):
        # Payload: ' OR '1'='1
        # Should NOT return all users
        with app.test_client() as client:
            response = client.get("/user?username=' OR '1'='1")
            # Once fixed, should handle safely
            assert len(response.get_json()) == 0 or response.status_code == 200

    def test_user_id_with_injection(self):
        # Payload: 1 OR 1=1
        with app.test_client() as client:
            response = client.get("/admin?user_id=1 OR 1=1")
            # Should return empty or single result, not admin bypass
            assert response.status_code == 200

class TestNoSQLInjectionPrevention:
    def test_mongodb_regex_injection(self):
        # Payload: {"$regex": ".*"}
        # Should not return all users
        result = find_user_by_email({"$regex": ".*"})
        # Once fixed, should be safe
        assert result is None or isinstance(result, dict)
    
    def test_mongodb_ne_injection(self):
        # Payload: {"$ne": null}
        result = find_user_by_id({"$ne": null})
        # Should not return all users
        assert result is None or isinstance(result, dict)
"""

    # File 4: Configuration file (red herring)
    codebase.files["config.py"] = """# Security configuration
# This is safe - just configuration, not executable
DB_TIMEOUT = 30
MAX_CONNECTIONS = 100
LOG_LEVEL = "INFO"
"""

    # File 5: Safe database wrapper (red herring - shows correct pattern)
    codebase.files["safe_db.py"] = """import sqlite3

def get_user_safe(username):
    # This is the CORRECT way - using parameterized queries
    # Not a vulnerability - this is the solution pattern!
    conn = sqlite3.connect('users.db')
    query = "SELECT * FROM users WHERE username = ?"
    cursor = conn.execute(query, (username,))
    return cursor.fetchall()
"""

def grade_task_2(codebase: SimulatedCodebase) -> float:
    """Grade Task 2: Check if SQL and NoSQL injections are fixed."""
    score = 0.0
    
    # 0.1: Read vulnerability files (discovery)
    if "app.py" in codebase.read_files or "mongo_handler.py" in codebase.read_files:
        score += 0.1
    
    # 0.15: Read both file types that need fixing
    if "app.py" in codebase.read_files and "mongo_handler.py" in codebase.read_files:
        score += 0.1
    
    # 0.2: SQL injection fixed (no f-strings with direct variables)
    if "app.py" in codebase.files:
        if 'f"SELECT' not in codebase.files["app.py"] and "f'SELECT" not in codebase.files["app.py"]:
            score += 0.15
    
    # 0.15: NoSQL injection fixed (proper ObjectId handling)
    if "mongo_handler.py" in codebase.files:
        if 'ObjectId(user_input)' not in codebase.files["mongo_handler.py"]:
            score += 0.12
    
    # 0.25: Security scan passes (no SQL or NoSQL injection detected)
    if codebase.security_scan and codebase.security_scan.passed:
        score += 0.25
    
    # 0.15: Tests pass (security assertions validate fixes)
    if codebase.unit_tests and codebase.unit_tests.passed:
        score += 0.15
    
    # Ensure score is strictly between 0 and 1 (exclusive)
    score = min(score, 0.99)
    score = max(score, 0.01)
    return score


# ============================================================================
# TASK 3: HARD - Cryptographic Weaknesses & Safe Patterns
# ============================================================================
# Real-world scenario: Migrating from weak to strong cryptography
# Difficulty: Agent must understand crypto best practices and handle legacy code

def setup_task_3(codebase: SimulatedCodebase):
    """Setup Task 3: Multiple cryptographic vulnerabilities."""
    
    # File 1: Authentication module with weak crypto
    codebase.files["auth.py"] = """import hashlib
import random
import string

# TODO: Replace MD5 with bcrypt before production!
def hash_password(password):
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

# TODO: Use secrets module instead!
def generate_session_token():
    # VULNERABLE: random is predictable
    chars = string.ascii_letters + string.digits
    token = ''.join(random.choice(chars) for _ in range(32))
    return token

# VULNERABLE: Hardcoded salt
def hash_with_salt(password):
    salt = "fixed_salt_12345"  # Hardcoded!
    return hashlib.md5((salt + password).encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed
"""

    # File 2: User database with weak credentials
    codebase.files["database.py"] = """import sqlite3
from auth import hash_password, hash_with_salt, generate_session_token

def create_user(username, password):
    # Using weak hashing function
    conn = sqlite3.connect('users.db')
    hashed = hash_password(password)  # MD5 - vulnerable!
    conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, hashed)
    )
    conn.commit()

def create_session(user_id):
    conn = sqlite3.connect('sessions.db')
    token = generate_session_token()  # Weak RNG - vulnerable!
    conn.execute(
        "INSERT INTO sessions (user_id, token) VALUES (?, ?)",
        (user_id, token)
    )
    conn.commit()
    return token

# Red herring: This is actually safe (parameterized query)
def get_user_safe(username):
    conn = sqlite3.connect('users.db')
    result = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    return result.fetchone()
"""

    # File 3: Configuration with crypto settings (red herring)
    codebase.files["config.py"] = """# Cryptography configuration
ENCRYPTION_ENABLED = False  # Red herring: just config, not executable
ALGO_CHOICE = "md5"  # Legacy choice
TOKEN_LENGTH = 32
HASH_ITERATIONS = 1
"""

    # File 4: Tests showing secure pattern (red herring)
    codebase.files["test_crypto.py"] = """import pytest
from unittest.mock import patch
from auth import hash_password, verify_password, generate_session_token

def test_password_hashing():
    # This test will fail until crypto is fixed
    password = "secure_password_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed), "Password verification failed"

def test_session_generation():
    # This test will fail until RNG is fixed
    token1 = generate_session_token()
    token2 = generate_session_token()
    assert token1 != token2, "Token generation is not unique"
    assert len(token1) == 32, "Token length incorrect"

def test_password_salt():
    # This test will fail until salt is made random
    p1 = hash_password("test")
    p2 = hash_password("test")
    assert p1 == p2, "Should be same for MD5, but should be different with proper salting"
"""

    # File 5: Migration guide (red herring - not executable)
    codebase.files["MIGRATION.md"] = """# Crypto Migration Guide

## Libraries needed:
- bcrypt for password hashing
- secrets for token generation
- cryptography for encryption

These are just comments - not security issues.
"""

def grade_task_3(codebase: SimulatedCodebase) -> float:
    """Grade Task 3: Check if cryptographic weaknesses are fixed."""
    score = 0.0
    
    # 0.1: Read vulnerability files
    if "auth.py" in codebase.read_files or "database.py" in codebase.read_files:
        score += 0.1
    
    # 0.15: Read both key files
    if "auth.py" in codebase.read_files and "database.py" in codebase.read_files:
        score += 0.1
    
    # 0.2: MD5 replaced with secure hash
    if "auth.py" in codebase.files:
        if "hashlib.md5" not in codebase.files["auth.py"] and "MD5(" not in codebase.files["auth.py"]:
            score += 0.15
    
    # 0.2: Weak RNG replaced with secrets
    if "auth.py" in codebase.files:
        if "random.choice" not in codebase.files["auth.py"] and "random.randint" not in codebase.files["auth.py"]:
            score += 0.15
    
    # 0.2: Hardcoded salt removed
    if "auth.py" in codebase.files:
        auth_content = codebase.files["auth.py"]
        if 'salt = "fixed_salt' not in auth_content and 'salt = \'fixed_salt' not in auth_content:
            score += 0.15
    
    # 0.25: Security scan passes (all crypto issues fixed)
    if codebase.security_scan and codebase.security_scan.passed:
        score += 0.25
    
    # 0.15: Tests pass (crypto functions work securely)
    if codebase.unit_tests and codebase.unit_tests.passed:
        score += 0.09
    
    # Ensure score is strictly between 0 and 1 (exclusive)
    score = min(score, 0.99)
    score = max(score, 0.01)
    return score

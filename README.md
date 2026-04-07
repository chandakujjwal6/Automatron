---
title: Automatron
emoji: 💻
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# DevSecOps Remediation Sandbox

**DevSecOps Remediation Sandbox** is a simulated CI/CD pipeline environment built for the OpenEnv standard. It challenges autonomous AI agents to act as DevSecOps engineers fixing security vulnerabilities in codebases.

Instead of playing a toy game, the agent must navigate a failing build: reading files, patching vulnerabilities (e.g., hardcoded secrets, command injection, buffer overflows), running security scans, and ensuring unit tests pass—all through a step-by-step interactive loop.

This environment implements the full OpenEnv specification, utilizing strictly typed Pydantic models for reliable Agent-Environment interaction.

---

## Observation Space (`state`)

When the agent calls `env.state()`, it receives a fully typed `CodebaseState` object representing the current snapshot of the codebase.

### Codebase State Overview

| Field | Data Type | Description |
| :--- | :--- | :--- |
| **`file_tree`** | `List[str]` | List of file paths in the codebase. |
| **`current_files`** | `List[FileInfo]` | Contents of files that have been read (path and content). |
| **`security_scan`** | `Optional[ScanResult]` | Result of the last security scan (tool, output, passed). |
| **`unit_tests`** | `Optional[TestResult]` | Result of the last unit test run (output, passed). |

### Nested Data Structures

* **`FileInfo`**: Contains `path` (str), `content` (str).
* **`ScanResult`**: Contains `tool` (str), `output` (str), `passed` (bool).
* **`TestResult`**: Contains `output` (str), `passed` (bool).

---

## Action Space (`step`)

The environment accepts a typed discriminated union of actions. The agent must pass one of the following structured JSON objects to `env.step(action)` to alter the state and fix vulnerabilities.

| Action Type (`action_type`) | Required Parameters | Description |
| :--- | :--- | :--- |
| **`read_file`** | `filepath` (str) | Read the content of the specified file. |
| **`search_and_replace`** | `filepath` (str), `old_snippet` (str), `new_snippet` (str) | Replace exact text in a file. |
| **`run_security_scan`** | None | Run a security scan on the codebase. |
| **`run_unit_tests`** | None | Run unit tests on the codebase. |

## Reward Function

- +0.2 for successfully reading a vulnerable file.
- +0.3 if security scan passes (vulnerabilities patched).
- +0.5 if unit tests pass (functionality preserved).
- -0.2 for failed search_replace (syntax errors).

## Scenarios & Tasks

The environment includes three progressively difficult scenarios, fulfilling the OpenEnv task requirements. Each task features a custom deterministic grader that outputs a score between `0.0` and `1.0`.

1. **Task 1: Easy (Python - The Leaked Secret)**
   * **Vulnerability:** Hardcoded API key in Python code.
   * **Objective:** Replace with `os.getenv()` and ensure tests pass.

2. **Task 2: Medium (Python - Command Injection)**
   * **Vulnerability:** Unsafe `subprocess.run(..., shell=True)`.
   * **Objective:** Use safe list-based arguments with `shell=False`.

3. **Task 3: Hard (C++ - Memory Safety)**
   * **Vulnerability:** Unsafe `strcpy` causing buffer overflow.
   * **Objective:** Replace with safe `std::string` or bounds-checking.

---

## Quick Start & Installation

You can run this environment locally or build the included Docker container.

### Option 1: Local Setup
1. Clone the repository and navigate to the directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Option 2: Docker
Build and run the evaluation agent inside a container:
   ```bash
   docker build -t devsecops-env .
   docker run -e OPENAI_API_KEY="your-api-key-here" devsecops-env
   ```

---

## Running the Autonomous Evaluation

This project includes a fully autonomous baseline agent (evaluate_agent.py) that uses a ReAct loop to solve the environment dynamically.

To watch the AI act as an autonomous DevSecOps engineer, run:
   ```bash
   python evaluate_agent.py
   ```

### Expected Output:
The script will initialize the environment, parse the CodebaseState JSON to the LLM, and execute the LLM's structured JSON decisions until vulnerabilities are fixed and a score of 1.0 is achieved for each task.

### Nested Data Structures
To parse the state effectively, the agent relies on the following sub-components:

* **`ProcessInfo`**: Contains `pid` (int), `name` (str), `user` (str), `cpu_percent` (float), and `open_files` (List[str]).
* **`NetworkConnection`**: Contains `conn_id` (str), `protocol` (str), `local_port` (int), `remote_ip` (str), `remote_port` (int), `state` (str), and an optional `associated_pid` (int).
* **`LogEntry`**: Contains `timestamp` (str), `source` (str), `message` (str), and `severity` (str).

---

## Action Space (`step`)

The environment accepts a typed discriminated union of actions. The agent must pass one of the following structured JSON objects to `env.step(action)` to alter the state of the server and mitigate threats.

| Action Type (`action_type`) | Required Parameters | Description |
| :--- | :--- | :--- |
| **`kill_process`** | `pid` (int) | Forcefully terminates the process matching the provided Process ID. |
| **`block_ip`** | `ip_address` (str) | Adds the specified IP address to the firewall blocklist, dropping active and future connections. |
| **`delete_file`** | `filepath` (str) | Deletes the specified file from the system (used for removing malicious binaries or scripts). |
| **`restart_service`** | `service_name` (str) | Restarts a legitimate system service (e.g., 'ssh', 'apache2') to apply patches or clear in-memory hooks. |
| **`wait`** | `duration` (int) | Pauses the agent for a specified number of seconds to observe how the system state evolves. |

## Scenarios & Tasks

The environment includes three progressively difficult scenarios, fulfilling the OpenEnv task requirements. Each task features a custom deterministic grader that outputs a score between `0.0` and `1.0`.

1. **Task 1: SSH Brute Force (Easy)**
   * **Threat:** A remote IP is repeatedly failing authentication attempts.
   * **Objective:** Read the system logs, identify the malicious IP, and execute a `block_ip` action.
2. **Task 2: Hidden Cryptominer (Medium)**
   * **Threat:** A process disguised as a system update is consuming 99% of the CPU and communicating with an external mining pool.
   * **Objective:** Identify the anomaly, execute `kill_process`, and `block_ip` on the C2 server. 
3. **Task 3: APT Backdoor (Hard)**
   * **Threat:** An attacker has established a reverse shell via a hidden cron job script.
   * **Objective:** The agent must dismantle the kill chain by killing the reverse shell process, blocking the attacker's IP, and executing `delete_file` to remove the persistence script.

---

## Quick Start & Installation

You can run this environment locally or build the included Docker container.

### Option 1: Local Setup
1. Clone the repository and navigate to the directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
3. Set your LLM API key as an environment variable (the baseline agent uses the Gemini API via OpenAI compatibility):
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
### Option 2: Docker
Build and run the evaluation agent inside a container:
   ```bash
   docker build -t cyberdefense-env .
   docker run -e GEMINI_API_KEY="your-api-key-here" cyberdefense-env
   ```
---

## Running the Autonomous Evaluation
This project includes a fully autonomous baseline agent (evaluate_agent.py) that uses a ReAct (Reasoning and Acting) loop to solve the environment dynamically.

To watch the AI act as an autonomous SOC analyst, run:
   ```bash
   python evaluate_agent.py
   ```
### Expected Output:
The script will initialize the environment, parse the ServerState JSON to the LLM, and execute the LLM's structured JSON decisions until the threat is neutralized and a score of 1.0 is achieved.
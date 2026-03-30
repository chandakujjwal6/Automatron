# CyberDefenseEnv

**CyberDefenseEnv** is a simulated Security Operations Center (SOC) environment built for the OpenEnv standard. It challenges autonomous AI agents to act as incident responders defending a simulated Linux server. 

Instead of playing a toy game, the agent must monitor realistic system telemetry—such as running processes, active network connections, and system logs—to detect anomalies. The agent must then take precise, targeted actions to mitigate cyber threats (like SSH brute-forcing, cryptominers, and APT backdoors) without disrupting legitimate system operations. 

This environment implements the full OpenEnv specification, utilizing strictly typed Pydantic models for reliable Agent-Environment interaction.

---

## Observation Space (`state`)

When the agent calls `env.state()`, it receives a fully typed `ServerState` object representing the current snapshot of the simulated server. 

### Server State Overview

| Field | Data Type | Description |
| :--- | :--- | :--- |
| **`system_load`** | `float` | Overall system CPU load percentage (0.0 to 100.0). |
| **`active_processes`** | `List[ProcessInfo]` | A list of all currently running processes on the server. |
| **`network_connections`** | `List[NetworkConnection]`| A list of all active incoming and outgoing network TCP/UDP connections. |
| **`recent_logs`** | `List[LogEntry]` | The last 50 lines of system logs (e.g., auth, syslog). |
| **`blocked_ips`** | `List[str]` | A list of IP addresses currently dropped by the server's firewall. |

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
   export GEMINI_API_KEY="your-api-key-here"
### Option 2: Docker
Build and run the evaluation agent inside a container:
   docker build -t cyberdefense-env .
   docker run -e GEMINI_API_KEY="your-api-key-here" cyberdefense-env

---

## Running the Autonomous Evaluation
This project includes a fully autonomous baseline agent (evaluate_agent.py) that uses a ReAct (Reasoning and Acting) loop to solve the environment dynamically.

To watch the AI act as an autonomous SOC analyst, run:
   python evaluate_agent.py

### Expected Output:
The script will initialize the environment, parse the ServerState JSON to the LLM, and execute the LLM's structured JSON decisions until the threat is neutralized and a score of 1.0 is achieved.
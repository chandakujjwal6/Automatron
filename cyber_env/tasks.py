from .simulator import SimulatedServer

# --- TASK 1: EASY (SSH Brute Force) ---
def setup_task_1(server: SimulatedServer):
    # Inject normal logs + malicious SSH logs
    server.logs.append({"timestamp": "10:00", "source": "sshd", "message": "Failed password for root from 192.168.1.100", "severity": "WARNING"})
    server.logs.append({"timestamp": "10:01", "source": "sshd", "message": "Failed password for root from 192.168.1.100", "severity": "WARNING"})
    
def grade_task_1(server: SimulatedServer) -> float:
    # Did they block the bad IP?
    if "192.168.1.100" in server.firewall_blocks:
        return 1.0
    return 0.0

# (Repeat for Task 2 and Task 3, writing setup and grade functions)

from .simulator import SimulatedServer
from .schemas import ProcessInfo, NetworkConnection

# --- TASK 2: MEDIUM (Cryptominer Eradication) ---

def setup_task_2(server: SimulatedServer):
    # 1. Inject a malicious process eating 99% CPU
    miner_pid = 31337
    server.processes.append(
        ProcessInfo(
            pid=miner_pid, 
            name="systemd-update", # Hiding in plain sight
            user="www-data", 
            cpu_percent=99.5, 
            open_files=["/tmp/.hidden_miner"]
        )
    )
    
    # 2. Inject the command-and-control network connection
    server.connections.append(
        NetworkConnection(
            conn_id="tcp_554", 
            protocol="TCP", 
            local_port=44532, 
            remote_ip="203.0.113.50", 
            remote_port=3333, 
            state="ESTABLISHED", 
            associated_pid=miner_pid
        )
    )
    
    # Push system load to critical
    server.load = 99.9 

def grade_task_2(server: SimulatedServer) -> float:
    score = 0.0
    
    # Did they kill the process?
    process_dead = not any(p.pid == 31337 for p in server.processes)
    if process_dead:
        score += 0.4
        
    # Did they block the mining pool IP?
    if "203.0.113.50" in server.firewall_blocks:
        score += 0.6
        
    return score

# --- TASK 3: HARD (APT Backdoor) ---

def setup_task_3(server: SimulatedServer):
    # The attacker dropped a script
    server.filesystem.append("/var/tmp/revshell.sh")
    
    # It executes via a hidden cron job, leaving a clue in the logs
    server.logs.append(
        {"timestamp": "03:00", "source": "CRON", "message": "CMD (/var/tmp/revshell.sh)", "severity": "INFO"}
    )
    
    # The active reverse shell process
    apt_pid = 1337
    server.processes.append(
        ProcessInfo(
            pid=apt_pid, 
            name="bash", 
            user="www-data", 
            cpu_percent=0.1, # Sneaky, low CPU
            open_files=["/var/tmp/revshell.sh"]
        )
    )
    
    # The active connection back to the attacker's machine
    server.connections.append(
        NetworkConnection(
            conn_id="tcp_999", 
            protocol="TCP", 
            local_port=54321, 
            remote_ip="198.51.100.99", 
            remote_port=4444, 
            state="ESTABLISHED", 
            associated_pid=apt_pid
        )
    )

def grade_task_3(server: SimulatedServer) -> float:
    score = 0.0
    
    # 1. Did they kill the reverse shell?
    if not any(p.pid == 1337 for p in server.processes):
        score += 0.3
        
    # 2. Did they block the attacker's IP?
    if "198.51.100.99" in server.firewall_blocks:
        score += 0.3
        
    # 3. Did they delete the malicious script?
    if "/var/tmp/revshell.sh" not in server.filesystem:
        score += 0.4
        
    return score
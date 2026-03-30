from .schemas import ServerState, ProcessInfo, LogEntry, NetworkConnection

class SimulatedServer:
    def __init__(self):
        self.load = 10.0
        self.processes = []
        self.connections = []
        self.logs = []
        self.firewall_blocks = []
        self.filesystem = [] # <--- NEW: Mock filesystem to track files

    def get_state(self) -> ServerState:
        return ServerState(
            system_load=self.load,
            active_processes=self.processes,
            network_connections=self.connections,
            recent_logs=self.logs[-50:],
            blocked_ips=self.firewall_blocks
        )

    def kill_process(self, pid: int):
        self.processes = [p for p in self.processes if p.pid != pid]
        self.logs.append(LogEntry(timestamp="now", source="kernel", message=f"Killed PID {pid}", severity="INFO"))

    def block_ip(self, ip: str):
        self.firewall_blocks.append(ip)
        self.connections = [c for c in self.connections if c.remote_ip != ip]
        
    # --- NEW METHOD ADDED BELOW ---
    def delete_file(self, filepath: str):
        if filepath in self.filesystem:
            self.filesystem.remove(filepath)
            self.logs.append(LogEntry(timestamp="now", source="kernel", message=f"Deleted file {filepath}", severity="INFO"))
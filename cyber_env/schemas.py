from pydantic import BaseModel, Field
from typing import List, Optional

# --- Sub-components of the System State ---

class ProcessInfo(BaseModel):
    pid: int = Field(description="Process ID")
    name: str = Field(description="Name of the executable")
    user: str = Field(description="User running the process (e.g., 'root', 'www-data')")
    cpu_percent: float = Field(description="Current CPU usage percentage")
    open_files: List[str] = Field(default_factory=list, description="Files currently opened by this process")

class NetworkConnection(BaseModel):
    conn_id: str = Field(description="Unique connection identifier")
    protocol: str = Field(description="TCP or UDP")
    local_port: int = Field(description="Local port number")
    remote_ip: str = Field(description="IP address of the remote connection")
    remote_port: int = Field(description="Port of the remote connection")
    state: str = Field(description="Connection state (e.g., 'ESTABLISHED', 'LISTEN', 'TIME_WAIT')")
    associated_pid: Optional[int] = Field(None, description="PID of the process owning this connection, if any")

class LogEntry(BaseModel):
    timestamp: str = Field(description="Time of the event")
    source: str = Field(description="Log source (e.g., 'auth.log', 'syslog', 'apache2')")
    message: str = Field(description="The actual log message content")
    severity: str = Field(description="INFO, WARNING, ERROR, or CRITICAL")

# --- The Main State Model ---

class ServerState(BaseModel):
    """The complete observable state of the simulated Linux server."""
    system_load: float = Field(description="Overall system CPU load (0.0 to 100.0)")
    active_processes: List[ProcessInfo] = Field(description="List of currently running processes")
    network_connections: List[NetworkConnection] = Field(description="List of active network connections")
    recent_logs: List[LogEntry] = Field(description="Last 50 lines of system logs")
    blocked_ips: List[str] = Field(default_factory=list, description="List of currently blocked IP addresses via firewall")

from typing import Literal, Union

class KillProcessAction(BaseModel):
    action_type: Literal["kill_process"] = "kill_process"
    pid: int = Field(description="The PID of the process to terminate")

class BlockIPAction(BaseModel):
    action_type: Literal["block_ip"] = "block_ip"
    ip_address: str = Field(description="The IP address to drop at the firewall")

class DeleteFileAction(BaseModel):
    action_type: Literal["delete_file"] = "delete_file"
    filepath: str = Field(description="The absolute path of the file to remove")

class RestartServiceAction(BaseModel):
    action_type: Literal["restart_service"] = "restart_service"
    service_name: str = Field(description="Name of the service to restart (e.g., 'ssh', 'apache2')")

class WaitAction(BaseModel):
    action_type: Literal["wait"] = "wait"
    duration: int = Field(description="Seconds to wait before taking another action, useful for observing changes")

# The unified Action type that the OpenEnv will accept
AgentAction = Union[
    KillProcessAction, 
    BlockIPAction, 
    DeleteFileAction, 
    RestartServiceAction, 
    WaitAction
]
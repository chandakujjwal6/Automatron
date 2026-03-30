from typing import Any, Dict
from .schemas import ServerState, AgentAction
from .simulator import SimulatedServer
from .tasks import setup_task_1, grade_task_1, setup_task_2, grade_task_2, setup_task_3, grade_task_3 # <--- Added Task 3 imports

class CyberDefenseEnv:
    def __init__(self, task_name: str = "task_1"):
        self.task_name = task_name
        self.server = SimulatedServer()
        self.reset()

    def reset(self):
        self.server = SimulatedServer()
        if self.task_name == "task_1":
            setup_task_1(self.server)
        elif self.task_name == "task_2":
            setup_task_2(self.server)
        elif self.task_name == "task_3":      # <--- Added route
            setup_task_3(self.server)

    def state(self) -> ServerState:
        return self.server.get_state()

    def step(self, action: AgentAction):
        if action.action_type == "kill_process":
            self.server.kill_process(action.pid)
        elif action.action_type == "block_ip":
            self.server.block_ip(action.ip_address)
        elif action.action_type == "delete_file":  # <--- Added action handler
            self.server.delete_file(action.filepath)
        
        self.server.load += 0.1 

    def score(self) -> float:
        if self.task_name == "task_1":
            return grade_task_1(self.server)
        elif self.task_name == "task_2":
            return grade_task_2(self.server)
        elif self.task_name == "task_3":      # <--- Added grading route
            return grade_task_3(self.server)
            
        return 0.0
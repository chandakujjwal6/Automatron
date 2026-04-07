from typing import Any, Dict, Tuple
from .schemas import CodebaseState, AgentAction, ReadFileAction, SearchReplaceAction, RunSecurityScanAction, RunUnitTestsAction
from .simulator import SimulatedCodebase
from .tasks import setup_task_1, grade_task_1, setup_task_2, grade_task_2, setup_task_3, grade_task_3

class DevSecOpsEnv:
    def __init__(self, task_name: str = "task_1"):
        self.task_name = task_name
        self.codebase = SimulatedCodebase()
        self.reset()
        self.done = False
        self.reward = 0.0

    def reset(self) -> CodebaseState:
        self.codebase = SimulatedCodebase()
        self.done = False
        self.reward = 0.0
        if self.task_name == "task_1":
            setup_task_1(self.codebase)
        elif self.task_name == "task_2":
            setup_task_2(self.codebase)
        elif self.task_name == "task_3":
            setup_task_3(self.codebase)
        return self.state()

    def state(self) -> CodebaseState:
        return self.codebase.get_state()

    def step(self, action: AgentAction) -> Tuple[CodebaseState, float, bool, Dict[str, Any]]:
        reward = 0.0
        info = {}

        if isinstance(action, ReadFileAction):
            success = self.codebase.read_file(action.filepath)
            if success:
                reward += 0.2  # Reward for investigating files
        elif isinstance(action, SearchReplaceAction):
            success = self.codebase.search_replace(action.filepath, action.old_snippet, action.new_snippet)
            if not success:
                reward -= 0.2  # Penalty for syntax/introduction errors
        elif isinstance(action, RunSecurityScanAction):
            self.codebase.run_security_scan()
            if self.codebase.security_scan and self.codebase.security_scan.passed:
                reward += 0.3
        elif isinstance(action, RunUnitTestsAction):
            self.codebase.run_unit_tests()
            if self.codebase.unit_tests and self.codebase.unit_tests.passed:
                reward += 0.5

        self.reward += reward
        self.done = self.score() >= 1.0

        return self.state(), reward, self.done, info

    def score(self) -> float:
        if self.task_name == "task_1":
            return grade_task_1(self.codebase)
        elif self.task_name == "task_2":
            return grade_task_2(self.codebase)
        elif self.task_name == "task_3":
            return grade_task_3(self.codebase)
        return 0.0
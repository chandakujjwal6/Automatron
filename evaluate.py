from cyber_env.env import DevSecOpsEnv
from cyber_env.schemas import ReadFileAction, SearchReplaceAction, RunSecurityScanAction, RunUnitTestsAction

# Initialize the env
env = DevSecOpsEnv(task_name="task_1")

# Example actions
action1 = ReadFileAction(filepath="app.py")
env.step(action1)

action2 = SearchReplaceAction(filepath="app.py", old_snippet='API_KEY = "sk-1234567890abcdef"', new_snippet="API_KEY = os.getenv('API_KEY')")
env.step(action2)

action3 = RunSecurityScanAction()
env.step(action3)

action4 = RunUnitTestsAction()
env.step(action4)

# Print Final Score
print("Final Score:", env.score())  # Should be 1.0
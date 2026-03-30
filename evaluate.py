from cyber_env.env import CyberDefenseEnv
from cyber_env.schemas import BlockIPAction

# Initialize the env
env = CyberDefenseEnv(task_name="task_1")

# Show initial state
print("Initial Logs:", env.state().recent_logs)

# Agent decides to act (Hardcoded baseline for demonstration)
action = BlockIPAction(ip_address="192.168.1.100")
env.step(action)

# Print Final Score
print("Final Score:", env.score()) # Should print 1.0
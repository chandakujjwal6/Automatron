#!/usr/bin/env python3
"""
DevSecOps OpenEnv Inference Script

Runs the autonomous agent against all 3 tasks with structured logging.
Follows the [START], [STEP], [END] format strictly for submission validation.
"""
import os
import json
import sys
from openai import OpenAI
from cyber_env.env import DevSecOpsEnv
from cyber_env.schemas import ReadFileAction, SearchReplaceAction, RunSecurityScanAction, RunUnitTestsAction

# ============================================================================
# ENVIRONMENT VARIABLES (MANDATORY)
# ============================================================================
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

if not HF_TOKEN:
    print("[ERROR] HF_TOKEN or OPENAI_API_KEY not provided")
    sys.exit(1)

# ============================================================================
# LOGGING FUNCTIONS (Per spec)
# ============================================================================

def log_start(model: str, tasks: list) -> None:
    """Log inference start."""
    data = {
        "type": "START",
        "model": model,
        "tasks": tasks
    }
    print(json.dumps(data))

def log_step(step: int, action: str, reward: float, done: bool, error: str = None) -> None:
    """Log individual step. Matches sample format exactly."""
    data = {
        "type": "STEP",
        "step": step,
        "action": action,
        "reward": reward,
        "done": done
    }
    if error:
        data["error"] = error
    print(json.dumps(data))

def log_end(success: bool, score: float, steps: int) -> None:
    """Log inference end."""
    data = {
        "type": "END",
        "success": success,
        "score": score,
        "steps": steps
    }
    print(json.dumps(data))

# ============================================================================
# INFERENCE LOOP
# ============================================================================

def main():
    """Main inference function."""
    
    # Initialize client
    client = OpenAI(
        api_key=HF_TOKEN,
        base_url=API_BASE_URL
    )
    
    # Log START
    tasks_list = ["task_1", "task_2", "task_3"]
    log_start(MODEL_NAME, tasks_list)
    
    # System prompt for agent
    system_prompt = """You are a DevSecOps engineer fixing security vulnerabilities.

Actions available:
- read_file (filepath)
- search_and_replace (filepath, old_snippet, new_snippet)
- run_security_scan ()
- run_unit_tests ()

Respond with JSON only: {"action_type": "...", ...}"""
    
    max_steps_per_task = 10
    total_rewards = []
    total_steps = 0
    
    for task_name in tasks_list:
        env = DevSecOpsEnv(task_name=task_name)
        env.reset()
        
        for step in range(1, max_steps_per_task + 1):
            total_steps += 1
            current_score = env.score()
            
            # Early exit if task complete
            if current_score >= 1.0:
                log_step(step=step, action="COMPLETE", reward=0.0, done=True)
                break
            
            # Get current state
            state_json = env.state().model_dump_json()
            
            try:
                # Call LLM
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": state_json}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                
                # Parse response
                content = response.choices[0].message.content.strip()
                if "```" in content:
                    content = content.split("```")[1].replace("json", "").strip()
                
                action_dict = json.loads(content)
                action_type = action_dict.get("action_type")
                
                # Execute action
                action_map = {
                    "read_file": ReadFileAction,
                    "search_and_replace": SearchReplaceAction,
                    "run_security_scan": RunSecurityScanAction,
                    "run_unit_tests": RunUnitTestsAction
                }
                
                if action_type not in action_map:
                    raise ValueError(f"Unknown action: {action_type}")
                
                action = action_map[action_type](**action_dict)
                obs, reward, done, info = env.step(action)
                
                total_rewards.append(reward)
                
                log_step(step=step, action=action_type, reward=reward, done=done)
                
                if done:
                    break
                    
            except Exception as e:
                log_step(step=step, action="ERROR", reward=0.0, done=False, error=str(e))
    
    # Final score calculation
    final_score = sum(total_rewards) / len(total_rewards) if total_rewards else 0.0
    final_score = min(max(final_score, 0.0), 1.0)
    success = final_score >= 0.5
    
    log_end(success=success, score=final_score, steps=total_steps)

if __name__ == "__main__":
    main()

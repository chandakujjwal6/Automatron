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

def log_start(task_name: str) -> None:
    """Log inference start with [START] marker."""
    print(f"[START] task={task_name}", flush=True)

def log_step(step: int, reward: float, done: bool, error: str = None) -> None:
    """Log individual step with [STEP] marker."""
    if error:
        print(f"[STEP] step={step} reward={reward:.2f} done={done} error={error}", flush=True)
    else:
        print(f"[STEP] step={step} reward={reward:.2f} done={done}", flush=True)

def log_end(task_name: str, score: float, steps: int) -> None:
    """Log inference end with [END] marker."""
    print(f"[END] task={task_name} score={score:.2f} steps={steps}", flush=True)

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
    
    # System prompt for agent (Enhanced for complex tasks)
    system_prompt = """You are an expert DevSecOps engineer fixing security vulnerabilities.

Your approach:
1. INVESTIGATE: Read files to understand the codebase structure
2. IDENTIFY: Run security scan to find vulnerabilities
3. REMEDIATE: Use search_and_replace to fix vulnerabilities
4. VALIDATE: Run unit tests to ensure fixes work
5. VERIFY: Run security scan again to confirm issues are resolved

Available actions:
- read_file (filepath): Read file contents to understand code
- search_and_replace (filepath, old_snippet, new_snippet): Fix vulnerabilities
- run_security_scan (): Scan for security issues
- run_unit_tests (): Validate fixes work correctly

Always respond with ONLY valid JSON: {"action_type": "...", "filepath": "...", ...}

For read_file: {"action_type": "read_file", "filepath": "filepath"}
For search_and_replace: {"action_type": "search_and_replace", "filepath": "filepath", "old_snippet": "...", "new_snippet": "..."}
For scans: {"action_type": "run_security_scan"} or {"action_type": "run_unit_tests"}

IMPORTANT:
- Read ALL files in the codebase first to understand dependencies
- Look for multiple vulnerabilities in different files
- Fix comprehensively, not just surface-level
- Use environment variables and safe patterns
- Test after every fix"""
    
    # Allow more steps for complex tasks (Task 1 and 2 have multiple files)
    max_steps_per_task = 20
    
    tasks_list = ["task_1", "task_2", "task_3"]
    
    for task_name in tasks_list:
        # Log task start
        log_start(task_name)
        
        env = DevSecOpsEnv(task_name=task_name)
        env.reset()
        
        task_rewards = []
        step_count = 0
        
        for step in range(1, max_steps_per_task + 1):
            step_count += 1
            current_score = env.score()
            
            # Early exit if task complete
            if current_score >= 1.0:
                log_step(step=step_count, reward=0.0, done=True)
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
                
                task_rewards.append(reward)
                
                log_step(step=step_count, reward=reward, done=done)
                
                if done:
                    break
                    
            except Exception as e:
                log_step(step=step_count, reward=0.0, done=False, error=str(e))
        
        # Log task end
        task_score = sum(task_rewards) / len(task_rewards) if task_rewards else 0.01
        # Ensure score is strictly between 0 and 1 (exclusive)
        task_score = min(max(task_score, 0.01), 0.99)
        log_end(task_name=task_name, score=task_score, steps=step_count)

if __name__ == "__main__":
    main()

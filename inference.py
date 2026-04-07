#!/usr/bin/env python3
"""
Structured inference script for DevSecOps Remediation Sandbox.
Follows [START], [STEP], [END] format as required by submission spec.
"""
import os
import json
import sys
from openai import OpenAI
from cyber_env.env import DevSecOpsEnv
from cyber_env.schemas import ReadFileAction, SearchReplaceAction, RunSecurityScanAction, RunUnitTestsAction

# Load environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("HF_TOKEN")

if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY or HF_TOKEN environment variable not set")
    sys.exit(1)

def run_inference():
    """Run inference on all 3 tasks with structured logging."""
    
    # [START] - Initialization
    print(json.dumps({
        "type": "START",
        "timestamp": "2024-01-01T00:00:00Z",
        "model": MODEL_NAME,
        "api_base": API_BASE_URL,
        "tasks": ["task_1", "task_2", "task_3"]
    }))
    
    # Initialize Gemini client
    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url=API_BASE_URL
    )
    
    tasks = ["task_1", "task_2", "task_3"]
    overall_score = 0.0
    
    for task_idx, task_name in enumerate(tasks):
        env = DevSecOpsEnv(task_name=task_name)
        
        system_prompt = """You fix code vulnerabilities in a DevSecOps sandbox.

Available actions:
1. read_file (filepath: str) - Read file content
2. search_and_replace (filepath: str, old_snippet: str, new_snippet: str) - Fix code
3. run_security_scan () - Run security scan
4. run_unit_tests () - Run unit tests

Always respond with JSON only. Example:
{"action_type": "read_file", "filepath": "app.py"}"""
        
        step_count = 0
        max_steps = 10
        
        while step_count < max_steps:
            step_count += 1
            current_score = env.score()
            
            # Check if task is complete
            if current_score >= 1.0:
                # [STEP] - Task complete
                print(json.dumps({
                    "type": "STEP",
                    "task": task_name,
                    "step": step_count,
                    "score": current_score,
                    "action": "COMPLETE",
                    "status": "success"
                }))
                break
            
            # Get current state
            state = env.state().model_dump_json()
            
            try:
                # Call Gemini API
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": state}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                
                # Parse response
                raw = response.choices[0].message.content.strip()
                if "```" in raw:
                    raw = raw.split("```")[1].replace("json", "").strip()
                
                action_data = json.loads(raw)
                action_type = action_data.get("action_type")
                
                # Map to action classes
                action_mapping = {
                    "read_file": ReadFileAction,
                    "search_and_replace": SearchReplaceAction,
                    "run_security_scan": RunSecurityScanAction,
                    "run_unit_tests": RunUnitTestsAction
                }
                
                if action_type not in action_mapping:
                    raise ValueError(f"Unknown action: {action_type}")
                
                # Execute action
                action_class = action_mapping[action_type]
                action = action_class(**action_data)
                env.step(action)
                
                # [STEP] - Action executed
                new_score = env.score()
                print(json.dumps({
                    "type": "STEP",
                    "task": task_name,
                    "step": step_count,
                    "score": new_score,
                    "action": action_type,
                    "status": "success"
                }))
                
            except Exception as e:
                # [STEP] - Error occurred
                print(json.dumps({
                    "type": "STEP",
                    "task": task_name,
                    "step": step_count,
                    "score": env.score(),
                    "action": "ERROR",
                    "error": str(e),
                    "status": "error"
                }))
        
        task_score = env.score()
        overall_score += task_score
    
    # [END] - Final results
    final_score = overall_score / len(tasks)
    print(json.dumps({
        "type": "END",
        "tasks_completed": len(tasks),
        "overall_score": final_score,
        "status": "complete"
    }))

if __name__ == "__main__":
    run_inference()

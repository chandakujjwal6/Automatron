import os
import json
from openai import OpenAI

# Import your environment and schemas
from cyber_env.env import DevSecOpsEnv
from cyber_env.schemas import (
    ReadFileAction, SearchReplaceAction, RunSecurityScanAction, RunUnitTestsAction
)

# Initialize the LLM Client using OpenAI API
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def run_autonomous_agent(task_name: str, max_steps: int = 10):
    """Run the autonomous DevSecOps agent on a specific task."""
    print(f"\n{'='*60}")
    print(f"Starting Autonomous Evaluation for {task_name.upper()}")
    print(f"{'='*60}\n")
    
    env = DevSecOpsEnv(task_name=task_name)
    
    # System prompt for the LLM
    system_prompt = """You are a DevSecOps AI fixing code vulnerabilities.

Available actions:
- read_file (filepath: str)
- search_and_replace (filepath: str, old_snippet: str, new_snippet: str)
- run_security_scan ()
- run_unit_tests ()

Respond with valid JSON only. Example: {"action_type": "read_file", "filepath": "app.py"}"""

    for step in range(max_steps):
        print(f"[Step {step + 1}] Current Score: {env.score():.2f}")
        
        # Check for early win
        if env.score() >= 1.0:
            print("\nAll vulnerabilities fixed! Agent wins.")
            break

        # Observe the state
        current_state = env.state()
        state_json = current_state.model_dump_json(indent=2)
        
        # Ask LLM for next action
        print("Agent is thinking...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CURRENT STATE:\n{state_json}\n\nWhat is your next action? Respond with JSON only."}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Extract and parse the JSON response
            llm_output = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if llm_output.startswith("```"):
                llm_output = llm_output.split("```")[1]
                if llm_output.startswith("json"):
                    llm_output = llm_output[4:]
                llm_output = llm_output.strip()
            
            # Parse JSON
            action_dict = json.loads(llm_output)
            action_type = action_dict.get("action_type")
            
            print(f"Agent Action: {action_type}")
            
            # Execute action
            if action_type == "read_file":
                action = ReadFileAction(**action_dict)
            elif action_type == "search_and_replace":
                action = SearchReplaceAction(**action_dict)
            elif action_type == "run_security_scan":
                action = RunSecurityScanAction(**action_dict)
            elif action_type == "run_unit_tests":
                action = RunUnitTestsAction(**action_dict)
            else:
                print(f"Invalid action type: {action_type}")
                continue
            
            # Step the environment
            observation, reward, done, info = env.step(action)
            print(f"Reward: {reward:+.2f} | Done: {done}\n")
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"LLM output: {llm_output if 'llm_output' in locals() else 'N/A'}\n")
        except Exception as e:
            print(f"Error: {str(e)}")
            if 'llm_output' in locals():
                print(f"LLM output: {llm_output}\n")
    
    # Final score
    final_score = env.score()
    print(f"{'='*60}")
    print(f"Final Score for {task_name}: {final_score:.2f}")
    print(f"{'='*60}\n")
    return final_score


if __name__ == "__main__":
    # Run evaluation on Task 1
    print("DevSecOps Remediation Sandbox - Autonomous Agent Evaluation\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        exit(1)
    
    score = run_autonomous_agent("task_1", max_steps=10)
    
    if score >= 1.0:
        print("SUCCESS: Task 1 completed!")
    else:
        print(f"INCOMPLETE: Task 1 score is {score:.2f}/1.0")
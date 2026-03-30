import os
import json
from openai import OpenAI
from pydantic import ValidationError

# Import your environment and schemas
from cyber_env.env import CyberDefenseEnv
from cyber_env.schemas import (
    KillProcessAction, BlockIPAction, DeleteFileAction, 
    RestartServiceAction, WaitAction
)

# Initialize the LLM Client using the Gemini API compatibility endpoint
# Replace this entire block
client = OpenAI(
    api_key="GEMINI_API_KEY", # <--- Hardcoded here!
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Define the models we want the LLM to know about
AVAILABLE_ACTIONS = {
    "kill_process": KillProcessAction.model_json_schema(),
    "block_ip": BlockIPAction.model_json_schema(),
    "delete_file": DeleteFileAction.model_json_schema(),
    "restart_service": RestartServiceAction.model_json_schema(),
    "wait": WaitAction.model_json_schema()
}

def run_autonomous_agent(task_name: str, max_steps: int = 5):
    print(f"\nStarting Autonomous Evaluation for {task_name.upper()}...")
    env = CyberDefenseEnv(task_name=task_name)
    
    # The System Prompt tells the LLM how to behave and what its constraints are
    system_prompt = f"""
    You are an autonomous Security Operations Center (SOC) agent.
    Your goal is to neutralize cyber threats on a Linux server without breaking legitimate services.
    
    You will be provided with the current ServerState in JSON format.
    Analyze the processes, connections, and logs to identify threats.
    
    You MUST respond with a SINGLE valid JSON object representing your chosen action.
    Do NOT include markdown formatting, backticks, or conversational text. Just the JSON.
    
    Here are the JSON schemas for the actions you are allowed to take:
    {json.dumps(AVAILABLE_ACTIONS, indent=2)}
    """

    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")
        
        # 1. Observe the State
        current_state = env.state()
        state_json = current_state.model_dump_json(indent=2)
        print(f"Server Load: {current_state.system_load}% | Score: {env.score()}")
        
        # Check for early win
        if env.score() >= 1.0:
            print("Threat completely neutralized! Agent wins.")
            break

        # 2. Prompt the LLM
        print("Agent is thinking...")
        try:
            response = client.chat.completions.create(
                model="gemini-2.5-flash", # Using the fast, reasoning-optimized Gemini model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CURRENT STATE:\n{state_json}\n\nWhat is your next action (output raw JSON)?"}
                ],
                temperature=0.1 # Low temperature for logical, deterministic choices
            )
            
            # Extract the JSON string from the LLM's response
            llm_output = response.choices[0].message.content.strip()
            
            # Clean up markdown if the LLM hallucinated it despite instructions
            if llm_output.startswith("```json"):
                llm_output = llm_output[7:-3].strip()
            elif llm_output.startswith("```"):
                llm_output = llm_output[3:-3].strip()
                
            action_dict = json.loads(llm_output)
            print(f"Agent Decided: {json.dumps(action_dict)}")
            
            # 3. Validate and Act
            action_type = action_dict.get("action_type")
            
            if action_type == "kill_process":
                action = KillProcessAction(**action_dict)
            elif action_type == "block_ip":
                action = BlockIPAction(**action_dict)
            elif action_type == "delete_file":
                action = DeleteFileAction(**action_dict)
            elif action_type == "restart_service":
                action = RestartServiceAction(**action_dict)
            elif action_type == "wait":
                action = WaitAction(**action_dict)
            else:
                print(f"LLM chose an invalid action type: {action_type}")
                env.step(WaitAction(duration=5))
                continue

            # Execute the validated Pydantic action in the environment
            env.step(action)
            
        except json.JSONDecodeError:
            print(f"Agent failed to output valid JSON. Raw output: {llm_output}")
            env.step(WaitAction(duration=5)) # Penalty wait
        except ValidationError as e:
            print(f"Agent output invalid parameters for the action: {e}")
            env.step(WaitAction(duration=5)) # Penalty wait
            
    print(f"\nFinal Evaluation Score for {task_name}: {env.score()}")

if __name__ == "__main__":
    print("Bypassing environment checks, using hardcoded API key...")
    
    # Run the agent against Task 1
    run_autonomous_agent(task_name="task_1", max_steps=3)
    
    # Uncomment to run against the harder tasks later:
    run_autonomous_agent(task_name="task_2", max_steps=5)
    run_autonomous_agent(task_name="task_3", max_steps=8)
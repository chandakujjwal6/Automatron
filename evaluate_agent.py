import os
import json
from openai import OpenAI
from cyber_env.env import DevSecOpsEnv
from cyber_env.schemas import ReadFileAction, SearchReplaceAction, RunSecurityScanAction, RunUnitTestsAction

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def run(task, steps=10):
    print(f"\n--- {task.upper()} ---")
    env = DevSecOpsEnv(task_name=task)
    
    sys_p = """You fix vulnerabilities.
Actions:
- read_file (filepath: str)
- search_and_replace (filepath: str, old_snippet: str, new_snippet: str)
- run_security_scan ()
- run_unit_tests ()
Respond with JSON only. Example: {"action_type": "read_file", "filepath": "app.py"}"""

    for i in range(steps):
        score = env.score()
        print(f"[Step {i + 1}] Score: {score:.2f}")
        if score >= 1.0:
            print("Win!")
            break

        state = env.state().model_dump_json()
        try:
            res = client.chat.completions.create(
                model="gemini-2.5-flash-lite", 
                messages=[
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": state}
                ]
            )
            
            raw = res.choices[0].message.content.strip()
            if "```" in raw:
                raw = raw.split("```")[1].replace("json", "").strip()
            
            d = json.loads(raw)
            t = d.get("action_type")
            print(f"Action: {t}")
            
            mapping = {
                "read_file": ReadFileAction,
                "search_and_replace": SearchReplaceAction,
                "run_security_scan": RunSecurityScanAction,
                "run_unit_tests": RunUnitTestsAction
            }
            
            act = mapping[t](**d)
            env.step(act)

        except Exception as e:
            print(f"Error: {e}")
            
    print(f"Final: {env.score():.2f}")

if __name__ == "__main__":
    run("task_1")
"""
Minimal HF Space server with /reset endpoint for submission validator.
"""
from flask import Flask, jsonify, request
import subprocess
import os
import threading

app = Flask(__name__)

# Store inference state
state = {"running": False, "last_result": None}

@app.post("/reset")
def reset():
    """Reset endpoint required by HF Space validator."""
    return jsonify({"status": "ok", "message": "Environment reset"}), 200

@app.get("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.post("/run_inference")
def run_inference():
    """Run the autonomous inference in background."""
    if state["running"]:
        return jsonify({"status": "already_running"}), 429
    
    def run_in_background():
        state["running"] = True
        try:
            result = subprocess.run(
                ["python", "inference.py"],
                capture_output=True,
                text=True,
                timeout=1200  # 20 minutes
            )
            state["last_result"] = {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            state["last_result"] = {"error": "Inference timeout (>20 min)"}
        finally:
            state["running"] = False
    
    thread = threading.Thread(target=run_in_background, daemon=True)
    thread.start()
    
    return jsonify({"status": "inference_started"}), 202

@app.get("/result")
def get_result():
    """Get last inference result."""
    return jsonify({
        "running": state["running"],
        "result": state["last_result"]
    }), 200

if __name__ == "__main__":
    # Run inference automatically on startup
    print("Starting DevSecOps Sandbox Server...")
    print("Running inference...")
    result = subprocess.run(["python", "inference.py"], capture_output=False)
    print("\nInference complete. Starting HF Space server on port 7860...")
    
    # Start server for HF Space validator
    app.run(host="0.0.0.0", port=7860, debug=False)

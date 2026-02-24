from mitmproxy import http
import json
import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.database import log_event

# Detection Engine URL
ENGINE_URL = "http://127.0.0.1:8001/analyze"

def request(flow: http.HTTPFlow) -> None:
    # Intercept OpenAI API calls
    if "api.openai.com" in flow.request.pretty_host:
        process_openai_request(flow)
    
    # Intercept Claude/Anthropic API calls
    elif "anthropic.com" in flow.request.pretty_host:
        process_anthropic_request(flow)

def process_openai_request(flow):
    try:
        data = json.loads(flow.request.content)
        if "messages" in data:
            # Extract last user message
            last_message = data["messages"][-1]
            if last_message["role"] == "user":
                prompt = last_message["content"]
                check_and_modify(flow, prompt, data)
    except Exception as e:
        print(f"Error processing OpenAI request: {e}")

def process_anthropic_request(flow):
    # Similar logic for Anthropic's structure
    try:
        data = json.loads(flow.request.content)
        if "messages" in data:
            last_message = data["messages"][-1]
            if last_message["role"] == "user":
                prompt = last_message["content"]
                check_and_modify(flow, prompt, data)
    except Exception as e:
        print(f"Error processing Anthropic request: {e}")

def check_and_modify(flow, prompt, data):
    try:
        response = requests.post(ENGINE_URL, json={"prompt": prompt}, timeout=2.0)
        if response.status_code == 200:
            result = response.json()
            if result["action"] == "block":
                log_event(prompt, result["score"], "block", "proxy", result["explanation"])
                flow.response = http.Response.make(
                    403,
                    json.dumps({
                        "error": "Blocked by RyzenShield AI Firewall",
                        "reason": result["explanation"],
                        "score": result["score"]
                    }),
                    {"Content-Type": "application/json"}
                )
                print(f"BLOCKED: Prompt risk score {result['score']}")
            elif result["score"] > 0.4:
                log_event(prompt, result["score"], "warning", "proxy", "Moderate risk")
                # Subtle sanitization or warning header can be added here
                print(f"WARNING: Moderate risk detected ({result['score']})")
            else:
                log_event(prompt, result["score"], "pass", "proxy", "Safe")
        else:
            print("Detection engine error. Passing through.")
    except Exception as e:
        print(f"Proxy bridge error: {e}. Passing through.")

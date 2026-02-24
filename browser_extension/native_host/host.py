import sys
import json
import struct
import requests

# This script communicates with the browser extension via standard I/O
# and forwards prompts to the local detection engine.

ENGINE_URL = "http://127.0.0.1:8001/analyze"

def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack('@I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def send_message(message):
    content = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('@I', len(content)))
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()

def main():
    while True:
        try:
            msg = get_message()
            if "prompt" in msg:
                # Forward to engine with a 2s timeout
                response = requests.post(ENGINE_URL, json={"prompt": msg["prompt"]}, timeout=2.0)
                if response.status_code == 200:
                    send_message(response.json())
                else:
                    send_message({"action": "error", "explanation": "Engine unreachable"})
        except Exception as e:
            send_message({"action": "error", "explanation": str(e)})

if __name__ == "__main__":
    main()

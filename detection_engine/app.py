from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import PromptGuardEngine
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

app = FastAPI()

# Model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "prompt-guard", "model.quant.onnx")
MAX_PROMPT_LENGTH = 10000  # Security: Limit input size to prevent DoS

# Global engine instance
engine = None

@app.on_event("startup")
async def startup_event():
    global engine
    try:
        engine = PromptGuardEngine(MODEL_PATH)
        print(f"Engine successfully initialized with model: {MODEL_PATH}")
    except Exception as e:
        import traceback
        traceback.print_exc()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/analyze")
async def analyze_prompt(request: PromptRequest):
    if not engine:
        raise HTTPException(status_code=500, detail="Detection Engine not initialized.")
    
    if len(request.prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(status_code=400, detail="Prompt too long.")
    
    result = engine.analyze(request.prompt)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

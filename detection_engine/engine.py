from transformers import AutoTokenizer
import onnxruntime as ort
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.database import log_event

# Auto-detect Ryzen AI SDK firmware path
sdk_base = r"C:\AMD\RyzenAI"
if not os.environ.get("XLNX_VART_FIRMWARE"):
    for root, dirs, files in os.walk(sdk_base):
        if "column_weights.bin" in files:
            os.environ["XLNX_VART_FIRMWARE"] = root
            print(f"NPU SDK: Auto-detected firmware at {root}")
            break


class PromptGuardEngine:
    def __init__(self, model_path, tokenizer_path=None):
        if tokenizer_path is None:
            # Point to the local directory where tokenizer files were downloaded
            tokenizer_path = os.path.dirname(model_path)
            
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        # Try to use VitisAIExecutionProvider for Ryzen AI NPU
        # Fallback to CPU if not available
        try:
            config_path = os.path.join(os.path.dirname(__file__), "vaip_config.json")
            self.session = ort.InferenceSession(
                model_path,
                providers=["VitisAIExecutionProvider", "CPUExecutionProvider"],
                provider_options=[{
                    "config_file": config_path,
                    "target": "RyzenAI-Phoenix"
                }, {}]
            )
        except Exception:
            self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

    def analyze(self, text):
        # Force add_special_tokens=True for Prompt Guard 2 tokenizer compatibility
        inputs = self.tokenizer(text, return_tensors="np", truncation=True, max_length=512, add_special_tokens=True)

        
        # Prepare all inputs required by the model
        ort_inputs = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"]
        }
        
        # Run inference
        outputs = self.session.run(None, ort_inputs)
        
        # Calculate probabilities using numerically stable softmax
        logits = outputs[0][0]
        logits_max = np.max(logits)
        exp_logits = np.exp(logits - logits_max)
        probs = exp_logits / np.sum(exp_logits)
        
        # Binary model: 0: Benign, 1: Insecure/Malicious
        risk_score = float(probs[1])
        
        # Action logic
        action = "block" if risk_score > 0.5 else "pass"
        explanation = "Safe prompt"
        if risk_score > 0.5:
            explanation = f"Potential prompt attack detected (Score: {risk_score:.2f})"
            
        # Log to database
        log_event(text, risk_score, action, "engine", explanation)
        
        return {
            "score": risk_score,
            "action": action,
            "explanation": explanation,
            "detail": {
                "benign": float(probs[0]),
                "insecure": float(probs[1])
            }
        }

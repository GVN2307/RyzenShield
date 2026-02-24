import os
from huggingface_hub import login, snapshot_download

def download():
    print("--- RyzenShield Model Downloader ---")
    print("The Llama Prompt Guard 2 model is gated and requires a Hugging Face token.")
    print("You can get one at: https://huggingface.co/settings/tokens")
    
    token = input("Enter your Hugging Face Token (leave blank if already logged in): ").strip()
    
    if token:
        login(token=token)
    
    repo_id = "meta-llama/Llama-Prompt-Guard-2-22M"
    local_dir = "./models/prompt-guard"
    
    print(f"\nDownloading {repo_id} to {local_dir}...")
    try:
        snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            allow_patterns=["onnx/*", "tokenizer*"]
        )
        print("\n[SUCCESS] Download complete. You can now run the detection engine.")
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        print("Make sure you have accepted the license terms on the Hugging Face model page:")
        print(f"https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    download()

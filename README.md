# RyzenShield AI Firewall Setup Guide

## 1. Prerequisites
- AMD Ryzen AI NPU enabled system.
- Python 3.9+
- Google Chrome or Brave Browser.

## 2. Installation
1.  Clone the repository and enter the directory.
2.  Create and activate a virtual environment:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Download the Llama Prompt Guard 2 22M model:
   ```bash
   python -m huggingface_hub.commands.huggingface_cli download meta-llama/Prompt-Guard-2-22M --include "onnx/*" --local-dir ./models/prompt-guard
   ```
   *Note: You may need a Hugging Face token for this gated repository.*

## 3. Browser Extension Setup
1. Open Chrome and go to `chrome://extensions`.
2. Enable "Developer mode".
3. Click "Load unpacked" and select the `browser_extension` folder.
4. Note your Extension ID (e.g., `abcdefghijklmnopqrstuvwxyz`).
5. Open `browser_extension/native_host/com.ryzenshield.firewall.json` and replace `PASTE_YOUR_EXTENSION_ID_HERE` with your ID.
6. Register the native host (Windows):
   - Run the following command in PowerShell as Administrator:
     ```powershell
     New-Item -Path "HKCU:\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.ryzenshield.firewall" -Value "[YOUR_PATH]\browser_extension\native_host\com.ryzenshield.firewall.json" -Force
     ```

## 4. Running the Firewall
1. Start the Detection Engine:
   ```bash
   cd detection_engine
   python app.py
   ```
2. Start the Local Proxy:
   ```bash
   cd local_proxy
   mitmdump -s proxy_addon.py
   ```
3. Configure your browser to use the proxy (usually `localhost:8080`).
4. **Critical**: Install the mitmproxy CA certificate for SSL inspection:
   - Locate the cert at `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.p12`.
   - Double-click the file $\rightarrow$ Select "Local Machine" $\rightarrow$ Next.
   - Password is blank $\rightarrow$ Next.
   - Select "Place all certificates in the following store" $\rightarrow$ Browse $\rightarrow$ **Trusted Root Certification Authorities**.
   - Finish.
   - *Restart your browser* to ensure Claude.ai and ChatGPT accept the intercepted traffic.


## 5. Usage
- Go to ChatGPT or Claude.
- The extension will automatically intercept your prompts and check them against the NPU-accelerated detection engine.
- High-risk prompts will be blocked before they reach the API.

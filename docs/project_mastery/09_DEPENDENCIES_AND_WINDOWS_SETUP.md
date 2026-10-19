# Trustwire — Dependencies, Runtime Environment & Windows Setup Guide

> **Target OS:** Windows 10 / Windows 11 (64-bit, x86_64)  
> **Python Runtime:** Python 3.11.9 (Recommended: Standard Windows Installer)  
> **Desktop Runtime:** Node.js 18+ LTS / Electron 30+  

---

## 1. Complete Dependency Inventory

### A. Python Backend Dependencies (`requirements.txt`)

| Package Name | Specific Version / Constraint | Primary Purpose in Trustwire |
| :--- | :--- | :--- |
| **`fastapi`** | `>=0.110.0` | High-performance asynchronous web framework for REST API & WebSockets. |
| **`uvicorn[standard]`** | `>=0.29.0` | ASGI web server running the event loop on `127.0.0.1:8765`. |
| **`torch`** | `>=2.2.0` | PyTorch deep learning framework executing the Wav2Vec2 audio classifier. |
| **`transformers`** | `>=4.40.0` | HuggingFace pipeline for Wav2Vec2 feature extraction and model loading. |
| **`onnxruntime`** | `>=1.17.0` | High-performance, SIMD-accelerated inference engine for Vision Transformer. |
| **`av` (PyAV)** | `>=12.0.0` | FFmpeg Python C-bindings for demuxing, video decoding, and audio resampling. |
| **`opencv-python`** | `>=4.9.0` | Computer vision library for Haar face cascades, YCrCb skin filter, Canny edges. |
| **`mss`** | `>=9.0.1` | Ultra-fast Windows GDI/DirectX desktop screen frame capture. |
| **`soundcard`** | `>=0.4.3` | Low-level CFFI wrapper for Windows WASAPI audio loopback streaming. |
| **`numpy`** | `>=1.26.0` | Multidimensional numerical array manipulation for tensors and frame buffers. |
| **`scipy`** | `>=1.13.0` | Signal processing routines (cross-correlation, filtering). |
| **`faster-whisper`** | `>=1.0.0` | CTranslate2-accelerated Whisper automatic speech recognition for fraud analysis. |
| **`pydantic`** | `>=2.6.0` | Data validation and settings management (`backend/config.py`). |
| **`pytest`** | `>=8.0.0` | Automated test runner executing the 22-test validation suite. |
| **`python-multipart`**| `>=0.0.9` | Streaming multipart/form-data parser for media file uploads. |

### B. Frontend & Electron Dependencies (`package.json`, `frontend/package.json`)

| Package Name | Category | Primary Purpose |
| :--- | :--- | :--- |
| **`electron`** | Desktop Shell | Native Windows application window, splash screen, and OS toasts. |
| **`react` & `react-dom`** | Frontend Framework | Declarative component UI running on React 18. |
| **`tailwindcss`** | CSS Framework | Responsive, modern dark-mode forensic styling. |
| **`lucide-react`** | Iconography | High-clarity vector icons for forensic indicators and alerts. |
| **`axios`** | HTTP Client | REST communication with backend attaching capability tokens. |
| **`vite`** | Build Tool | Ultra-fast HMR dev server and optimized production bundler. |
| **`typescript`** | Type System | Static typing for forensic data models and API response contracts. |

---

## 2. Hardware & System Requirements

| Specification | Minimum Required | Recommended Production Workstation |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 Home/Pro 64-bit | Windows 11 Pro 64-bit |
| **CPU Architecture** | x86_64 with AVX2 support (Intel 6th Gen / AMD Ryzen 1000) | 8+ Cores with AVX-512 (Intel 12th+ Gen / AMD Ryzen 5000+) |
| **System Memory (RAM)**| 8 GB DDR4 | 16 GB or 32 GB DDR4/DDR5 |
| **Disk Storage** | 3.0 GB free SSD storage | 10.0 GB NVMe SSD |
| **Display Resolution**| 1280 x 720 (720p) | 1920 x 1080 (1080p) or higher |
| **Audio Hardware** | Default Windows Soundcard | Realtek / Dedicated USB Audio Interface with WASAPI support |

---

## 3. Environment Variables Reference

Trustwire can be configured using environment variables set before execution:

- **`TRUSTWIRE_API_TOKEN`**: Custom security capability token. If omitted, Trustwire generates an ephemeral 32-character hex UUID on startup.
- **`PYTHON_PATH`**: Explicit path to the Python 3.11 executable (useful if multiple Python versions exist on the system):
  ```powershell
  $env:PYTHON_PATH = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
  ```
- **`TRUSTWIRE_PORT`**: Port for FastAPI backend (default: `8765`).
- **`TRUSTWIRE_DEV_NO_AUTH`**: Set to `"1"` during automated unit testing or headless development to bypass capability token enforcement on REST routes.

---

## 4. Complete Step-by-Step Installation on Clean Windows Machine

### Step 1: Install System Prerequisites
1. Download and install **Python 3.11.9 (64-bit)** from [python.org](https://www.python.org).
   > **CRITICAL:** Check the box **"Add python.exe to PATH"** during installation.
2. Download and install **Node.js 18+ or 20+ LTS** from [nodejs.org](https://nodejs.org).
3. Install the **Microsoft Visual C++ 2015–2022 Redistributable (x64)** (required by PyAV, OpenCV, and ONNX Runtime).

### Step 2: Clone Repository & Setup Virtual Environment
Open Windows PowerShell:
```powershell
# Navigate to desired directory
cd "C:\Users\Administrator\Desktop\VS Code\trustwire"

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and packaging tools
python -m pip install --upgrade pip setuptools wheel
```

### Step 3: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Install & Build Desktop Frontend
```powershell
# Install root electron dependencies
npm install

# Navigate to frontend, install, and build static assets
cd frontend
npm install
npm run build
cd ..
```

### Step 5: Verify Model Weights & Checkpoints
Ensure model directories exist on disk:
- `models/video/deepfake_v1/model.onnx`
- `models/audio/wav2vec2_v2/`
*(If checkpoints are missing, Trustwire automatically pulls them from official HuggingFace repositories on initial boot).*

### Step 6: Launch Full Desktop Application
```powershell
npm start
```
*Electron will spawn the splash screen, boot the FastAPI backend on port 8765, verify health, and open the full forensic workstation.*

---

## 5. Troubleshooting Windows-Specific Edge Cases

### Issue 1: `ImportError: DLL load failed while importing av`
- **Cause:** Missing Microsoft Visual C++ Runtime libraries required by PyAV's compiled FFmpeg binaries.
- **Fix:** Install `vcredist_x64.exe` from Microsoft's official download page and restart the shell.

### Issue 2: `soundcard` Fails to Enumerate WASAPI Loopback Devices
- **Cause:** The Windows audio service is disabled or no audio output endpoint is currently active.
- **Fix:** Ensure speakers or headphones are plugged in and playing test audio. Verify Windows Audio service is running:
  ```powershell
  Get-Service -Name AudioSrv
  ```

### Issue 3: High-DPI Scaling Distorts MSS Screen Capture
- **Cause:** Windows display scaling (125%, 150%) causes coordinate mismatch in GDI BitBlt.
- **Fix:** Trustwire's `screen.py` uses monitor-specific bounding rects from `mss.monitors`, which automatically handle DPI scaling offsets without manual registry overrides.

### Issue 4: Port 8765 Already in Use
- **Cause:** A stranded backend process from a previous crashed run is still holding the port.
- **Fix:** Kill the orphaned python process:
  ```powershell
  Stop-Process -Name python -Force
  ```

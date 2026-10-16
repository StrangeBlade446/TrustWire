# Trustwire

> **Detect deception before it costs you.**

Trustwire is an autonomous, privacy-conscious Windows desktop application combining three independent, local-first forensic capabilities:
1. **Deepfake Video Detection:** Neural inspection of video frames and facial regions for AI generation and manipulation artifacts.
2. **Deepfake Audio & Voice-Cloning Detection:** Acoustic spectral discrimination of synthetic speech, voice clones, and neural vocoder artifacts.
3. **Financial Fraud & Social-Engineering Detection:** Real-time conversational risk engine identifying coercive instructions, credential demands (OTP/PIN), urgency threats, and remote-access extortion.

All three systems operate independently—a failure or unavailability in one detector will never crash the others.

---

## Key Features

- **Real-Time Windows Desktop Shield:** Captures desktop screen regions and system playback audio via native Windows WASAPI loopback without webcam or microphone access.
- **Offline Media Forensic Inspection:** Drag-and-drop analysis for recorded media files (MP4, MKV, WebM, WAV, MP3, FLAC) with separated video, audio, and transcript inspection tracks.
- **100% Local Inference:** No audio, video, or transcripts are ever transmitted to cloud servers. Zero third-party telemetry.
- **Strict 15-Minute Maximum Retention:** Enforced by background cleanup workers, startup crash recovery, and instant manual purging.
- **Zero Raw Media in Alerts:** Alert logs store only forensic metadata, confidence scores, and action advice.
- **Localhost Capability Token Authentication:** Cryptographically defends the local API server against unauthorized local processes or browser tabs.
- **Zero Mock Policy:** Never fabricates random confidence scores, simulated model predictions, or mock detections in production features.

---

## System Requirements

- **Operating System:** Windows 10 or Windows 11 x64 (Windows 11 recommended).
- **Processor:** Modern x64 multi-core processor (Intel Core i5/i7/i9 or AMD Ryzen).
- **Memory (RAM):** Minimum 8 GB (16 GB recommended).
- **Disk Space:** ~2.5 GB free space (including models and dependencies).
- **Runtimes:** Python 3.11+ and Node.js v20+.
- **Media Engine:** FFmpeg in system PATH (verified with FFmpeg 6.0+ / 9.0+).

---

## Architecture Overview

Trustwire runs as a paired architecture:
- **Desktop Shell:** Electron with context isolation, auto-managing backend lifecycle and native Windows frame.
- **Frontend Interface:** React 18, TypeScript, Vite, Tailwind CSS, Lucide icons, dark graphite palette.
- **Backend Core:** FastAPI, Uvicorn, WebSockets event channel (`127.0.0.1:8765`).
- **Vision Inference:** Quantized Vision Transformer (ViT) via ONNX Runtime CPU (~205ms/frame).
- **Audio Inference:** Wav2Vec2 Audio Classifier via PyTorch CPU (~287ms/chunk).
- **Speech Engine:** Faster-Whisper (CTranslate2 int8) for local offline speech-to-text (~1140ms/chunk).
- **Capture Engine:** Windows WASAPI loopback (`soundcard`) & DirectX/GDI screen capture (`mss`).

---

## Installation & Launch Instructions

### 1. Clone the Repository
```powershell
git clone https://github.com/your-username/trustwire.git
cd trustwire
```

### 2. Install Python Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Install Node & Frontend Dependencies
```powershell
npm install
cd frontend
npm install
npm run build
cd ..
```

### 4. Launch Trustwire Desktop
Using PowerShell:
```powershell
.\scripts\launch.ps1
```
Or using the Windows Command Prompt / Double-click:
```cmd
.\scripts\launch.bat
```
Or directly via npm:
```powershell
npm start
```

---

## Supported Formats

- **Video Formats:** MP4, MOV, MKV, AVI, WebM
- **Audio Formats:** WAV, MP3, M4A, FLAC, OGG, AAC
- **Capture Sources:** Any active Windows desktop monitor; any active WASAPI speaker/headphone playback loopback.

---

## Model Provenance & Licenses

| Capability | Architecture | Checkpoint Source | License | Measured Runtime |
|------------|--------------|-------------------|---------|------------------|
| **Video Deepfake** | Vision Transformer (ViT) | `onnx-community/deepfake_vs_real_image_detection-ONNX` | Apache-2.0 | 205 ms / frame |
| **Audio Deepfake** | Wav2Vec2 Sequence Classifier | `MelodyMachine/Deepfake-audio-detection-V2` | MIT | 287 ms / chunk |
| **Speech-to-Text** | Whisper (tiny.en / tiny) | OpenAI / Systran `faster-whisper` | MIT | 1140 ms / chunk |
| **Fraud Rules Engine**| Contextual Multi-Vector Taxonomy | Trustwire Native Rules | MIT | 0.5 ms / check |

For complete documentation on model boundaries and third-party terms, see [`docs/MODELS_AND_LICENSES.md`](docs/MODELS_AND_LICENSES.md).

---

## How Live Monitoring Works

1. Open the **Live Monitoring** tab in the desktop application.
2. Select your desired display and WASAPI audio loopback device.
3. Configure which detectors to run (Video, Audio, Fraud Analysis).
4. Click **Start Live Monitoring**.
5. Trustwire captures screen frames and system audio into bounded in-memory queues (stale frames are dropped to eliminate latency).
6. When an anomaly is detected, high-confidence alerts are displayed in real time with recommended actions.
7. Stopping monitoring immediately halts all capture threads and purges active in-memory buffers.

---

## Running Automated Tests

Trustwire includes a comprehensive automated test suite with unit, model smoke, and integration tests:

```powershell
# Run full automated test suite
python -m pytest

# Run specific test modules
python -m pytest tests/test_fraud_engine.py
python -m pytest tests/test_retention.py
python -m pytest tests/test_detectors.py
python -m pytest tests/test_api.py
```

All 22 automated tests are verified to pass on Windows 11.

---

## Forensic Advisory & Probabilistic Notice

> **Important:** Deepfake detection, synthetic speech discrimination, and conversational fraud risk scoring are probabilistic heuristic techniques, not infallible mathematical proofs.
> A result of *"Likely authentic"* or *"No suspicious evidence detected"* does not guarantee authenticity or prove that an actor is genuine. Never use Trustwire as sole legal proof of identity or criminality. Always verify critical requests via trusted secondary channels.

---

## Privacy & Data Retention Guarantees

- **15-Minute Strict Retention:** Diagnostic artifacts expire and are deleted within 15 minutes.
- **Startup Scrubbing:** Crashed runs are cleaned up automatically on the next launch.
- **Zero Surveillance:** Trustwire never turns on your webcam or records your microphone.
- For complete privacy guarantees, see [`docs/PRIVACY.md`](docs/PRIVACY.md).

---

## Contributing & Security

- Contributions are welcome! Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.
- To report a security vulnerability, refer to [`SECURITY.md`](SECURITY.md).
- Original code is licensed under the [MIT License](LICENSE).

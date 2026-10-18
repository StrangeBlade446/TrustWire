# Trustwire

> **Detect deception before it costs you.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11%20x64-blue.svg)](https://microsoft.com/windows)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Electron: 32+](https://img.shields.io/badge/Electron-32%2B-brightgreen.svg)](https://electronjs.org)

**Trustwire** is an autonomous, on-device AI deception defense system and forensic deepfake shield built for Windows. It provides real-time active system monitoring and offline media analysis to protect users against generative AI deepfakes, synthetic speech cloning, and generative watermark tampering.

Developed for **Reforged '26** under the **AI/ML, Cybersecurity & Digital Trust** track by team **the omniscient**.

---

## 👥 Team Information — the omniscient

- **Rudra Veer Singh**
- **Daksh Pratap Singh**
- **Shivaksh Arya**
- **Suhel Khan**

*Official Pitch Deck:* [`TrustWire_Presentation_The_Omniscient.pptx`](TrustWire_Presentation_The_Omniscient.pptx)

---

## 🛡️ Core Capabilities

1. **Deepfake Video Detection:**
   - Evaluates video frames and facial regions using a fine-tuned **Vision Transformer (ViT)** (`224x224 RGB`, ~205ms CPU inference).
   - Multi-scale Canny edge correlation for detecting Google Gemini / SynthID 4-pointed star watermarks and generative artifacts.
   - Container metadata integrity validation via native PyAV/FFmpeg bindings.

2. **Deepfake Audio & Synthetic Voice Discrimination:**
   - Acoustic spectral feature discrimination using **INT8 Quantized Wav2Vec2 Large XLSR** (~140ms latency on CPU, 355 MB memory footprint).
   - Detects neural vocoder synthesis artifacts (ElevenLabs, Bark, Tortoise, VALL-E) across 16 kHz mono streams.

3. **Decoupled Architecture:**
   - **Offline Media Analysis:** Drag-and-drop file inspection for pre-recorded files (MP4, MOV, MKV, WAV, MP3, FLAC) with comprehensive forensic reports, timestamps, and confidence scores.
   - **Real-Time Live Monitoring:** Background screen grab (`mss`) and WASAPI loopback speaker audio capture (`soundcard`) with floating HUD overlay and disparity alerts over ongoing video calls.
   - Completely independent operational paths to eliminate cross-interference.

4. **100% On-Device Privacy:**
   - Zero cloud telemetry or external network calls.
   - Automated 15-minute ephemeral memory purge policy.
   - Never accesses user microphones or webcams (captures loopback output and monitor frames only).

---

## 🏗️ Technical Architecture

Trustwire runs as a 4-tier paired architecture:
- **Tier 1 (Capture & Ingest):** Screen capture worker (`mss` with 1-element queue to prevent lag), soundcard WASAPI loopback audio capture, and PyAV demuxer.
- **Tier 2 (Preprocessing):** Multi-cascade Haar face crop with adaptive 70px minSize, 16 kHz mono acoustic resampling, and bottom-right 28% frame watermark isolation.
- **Tier 3 (Neural Cores):** Vision Transformer (ViT) on CPU (SIMD/AVX2) and INT8 Quantized Wav2Vec2 audio classifier.
- **Tier 4 (Dispatch & HUD):** Central Alert Hub with deduplication cooldown, WebSocket event broadcasting, and Electron desktop shell with React 18 UI.

---

## 💻 System Requirements

- **Operating System:** Windows 10 or Windows 11 x64 (Windows 11 recommended).
- **Processor:** Modern x64 multi-core processor (Intel Core i5/i7/i9 or AMD Ryzen).
- **Memory (RAM):** Minimum 8 GB (16 GB recommended).
- **Disk Space:** ~2.5 GB free space (including models and dependencies).
- **Runtimes:** Python 3.11+ and Node.js v20+.
- **Media Engine:** FFmpeg in system PATH.

---

## 🚀 Installation & Launch Instructions

### 1. Clone the Repository
```powershell
git clone https://github.com/hash-StrangeBlade/TrustWire.git
cd TrustWire
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
Or using Command Prompt / Double-click:
```cmd
.\scripts\launch.bat
```
Or directly via npm:
```powershell
npm start
```

---

## 📊 Model Provenance & Citations

| Capability | Architecture | Upstream / Citation | License | Device / Latency |
|------------|--------------|---------------------|---------|------------------|
| **Video Deepfake** | Vision Transformer (ViT) | Dosovitskiy et al., ICLR 2021 (`deepfake_vs_real_image_detection-ONNX`) | Apache-2.0 | CPU (SIMD/AVX2) ~205ms |
| **Audio Deepfake** | Wav2Vec 2.0 Large XLSR | Baevski et al., NeurIPS 2020 / ASVspoof Benchmark | MIT | CPU (INT8 Quantized) ~140ms |
| **Watermark Match** | Multi-Scale Edge Correlation | Google DeepMind SynthID Imperceptible Watermarking Specification | Open | CPU ~12ms |

For complete documentation on model boundaries and third-party terms, see [`docs/MODELS_AND_LICENSES.md`](docs/MODELS_AND_LICENSES.md).

---

## 🧪 Automated Testing

Trustwire includes a comprehensive automated test suite verifying endpoints, calibration thresholds, and detector performance:

```powershell
# Run full automated test suite
python -m pytest

# Run detector calibration tests
python -m pytest tests/test_detectors.py
python -m pytest tests/test_api.py
```

---

## 🔒 Privacy & Data Retention Guarantees

- **15-Minute Strict Retention:** Diagnostic artifacts expire and are deleted within 15 minutes.
- **Startup Crash Recovery:** Any stranded temp files from previous sessions are purged on launch.
- **Zero Raw Media in Alerts:** Alert logs store only forensic metadata, confidence scores, and action advice.
- For complete privacy guarantees, see [`docs/PRIVACY.md`](docs/PRIVACY.md).

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

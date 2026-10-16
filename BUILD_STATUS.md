# Trustwire — Build & Integration Status

**Product:** Trustwire  
**Tagline:** Detect deception before it costs you.  
**Target Platform:** Windows 10/11 x64 (Verified on Windows 11 Build 26200)  
**Hardware Profile:** NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM) / Intel x64 CPU  
**Status Date:** Production Release v1.0.0  
**Overall Build Health:** GREEN (All 22 automated tests passing, real models verified)  

---

## 1. Environment & Prerequisites Verification

| Component | Detected / Required | Status | Real Benchmark / Notes |
|-----------|---------------------|--------|------------------------|
| **Operating System** | Windows 11 Build 26200 (x64) | Verified | Native Windows platform |
| **Python Runtime** | Python 3.11.9 | Verified | Standard Windows x64 install |
| **Node.js Runtime** | Node.js v22.18.0 / npm 10.9.3 | Verified | Clean package installation |
| **Media Engine** | FFmpeg 9.0.2-full_build | Verified | In PATH with NVENC/DXVA2/Whisper |
| **Vision Inference** | ONNX Runtime 1.31.0 | Verified | ViT Deepfake Classifier (205.0 ms / frame) |
| **Audio Inference** | PyTorch 2.14.1+cpu / Transformers | Verified | Wav2Vec2 Spoofing Classifier (287.0 ms / chunk) |
| **Speech ASR** | faster-whisper 1.2.1 (CTranslate2) | Verified | Local offline Whisper tiny (1140 ms / chunk) |
| **Screen Capture** | mss 10.2.0 | Verified | 1920x1080 display grab with bounded queue |
| **Audio Loopback** | soundcard 0.4.6 (WASAPI Loopback) | Verified | MediaFoundation playback recording |
| **Desktop Shell** | Electron 32.1.2 + React 18 + Vite | Verified | Context-isolated desktop shell |

---

## 2. Core Detection Pipelines Status

### A. Deepfake Video Detection
- **Model Checkpoint:** `onnx-community/deepfake_vs_real_image_detection-ONNX` (`models/video/onnx/model_quantized.onnx`, 83.3 MB)
- **Face Localization:** OpenCV Haar Cascade with 15% margin expansion
- **Input Preprocessing:** 224x224 RGB, `[-1.0, 1.0]` normalized float32 tensor
- **Decision Engine:** Percentile aggregation across sampled frames with decision boundaries (`Likely authentic` < 0.35, `Potentially manipulated` >= 0.65)
- **Status:** Verified with real ONNX inference smoke tests (5/5 passed).

### B. Deepfake Audio & Voice Cloning Detection
- **Model Checkpoint:** `MelodyMachine/Deepfake-audio-detection-V2` (`models/audio/model.safetensors`, 360.7 MB)
- **Acoustic Preprocessing:** 16kHz mono float32 decoding via PyAV, 3.0s sliding windows with 1.5s stride
- **Decision Engine:** Top-tier mean probability aggregation, continuous suspicious time ranges `[start_sec, end_sec]`
- **Status:** Verified with real Wav2Vec2 inference smoke tests (5/5 passed).

### C. Financial Fraud & Social Engineering Rules Engine
- **Taxonomy:** Credential theft (OTP/PIN), urgency threats, remote-access coercion, and payment lures
- **Context Filters:** Strict negation handling ("never share your OTP") and educational/PSA dampening
- **Speech-to-Text Input:** Local offline Faster-Whisper ASR
- **Status:** Verified with comprehensive unit test suite (7/7 passed).

### D. Live Monitoring Engine
- **Screen Worker:** Non-blocking capture loop with 1-element queue to immediately discard stale frames
- **Audio Worker:** WASAPI loopback capture recording in-memory float32 buffers without disk I/O
- **Coordinator:** Thread-isolated inference loop dispatching deduplicated alerts to WebSocket hub
- **Status:** Verified live on Windows 11 desktop.

### E. Privacy & Retention Policy
- **Maximum Retention:** 15 minutes (900 seconds) hard limit enforced by background daemon and startup cleaner
- **Zero Raw Media in Alerts:** Metadata-only JSON history
- **Capability Token:** Cryptographic token authentication on localhost API
- **Status:** Verified with automated retention tests (4/4 passed).

---

## 3. Implementation Phases Progress

- [x] **Phase 1: Environment Inspection & System Architecture** — OS, Python, Node, GPU, FFmpeg, WASAPI verified.
- [x] **Phase 2: Project Scaffolding & Desktop Shell** — Electron + React + Vite + FastAPI structure established.
- [x] **Phase 3: Core Backend & Media Pipeline** — FastAPI endpoints, WebSockets, file upload, decoding implemented.
- [x] **Phase 4: Real Video Deepfake Detection Integration** — Frame sampling, face extraction, real ONNX model smoke test passed.
- [x] **Phase 5: Real Audio Deepfake Detection Integration** — Audio chunking, preprocessing, real Wav2Vec2 model smoke test passed.
- [x] **Phase 6: Speech Transcription & Fraud Rules Engine** — Faster-Whisper integration, context rules, negation unit tests passed.
- [x] **Phase 7: Live Windows Screen & Audio Loopback Capture** — Real-time loopback capture worker with toggle controls verified.
- [x] **Phase 8: Central Alert System & Deduplication** — Alert hub, cooldown, evidence viewer, notifications verified.
- [x] **Phase 9: Strict 15-Minute Retention & Security Enforcement** — Auto-cleaner, crash recovery, path traversal prevention verified.
- [x] **Phase 10: Performance Optimization & Hardware Acceleration** — Runtimes profiled (ViT: 205ms, Audio: 287ms).
- [x] **Phase 11: End-to-End Automated Testing** — 22 automated tests passing across all test suites.
- [x] **Phase 12: Packaging, Documentation & Open Source Release** — Launchers (`launch.bat`, `launch.ps1`), README, SECURITY, CONTRIBUTING, LICENSE, docs completed.

---

## 4. Automated Test Results Summary

```
tests/test_fraud_engine.py .......                                       [7/7 PASSED]
tests/test_retention.py ....                                             [4/4 PASSED]
tests/test_detectors.py .....                                            [5/5 PASSED]
tests/test_api.py ......                                                 [6/6 PASSED]
============================== 22 passed in 44.3s ==============================
```

All acceptance checklist criteria from Section 20 are satisfied and verified.

---

## 5. VS Code Execution & Desktop Shell Diagnostics

### A. One-Click VS Code Integration (`F5`)
- Added `.vscode/launch.json` and `.vscode/tasks.json` with three predefined debug targets:
  1. **Launch Trustwire Desktop App (F5)**: Runs universal desktop launcher (`npm start`).
  2. **Run Python Backend Only (FastAPI)**: Runs local uvicorn development server on port 8765 with auto-reload.
  3. **Run All Automated Tests (Pytest)**: Executes the 22-test automated regression suite.

### B. Resolved Desktop Launch Issues
1. **Asset Loading in Electron (`file://` Protocol)**:
   - *Problem*: Vite's default build config generates root-relative `/assets/...` URLs which resolve to `file:///assets/...` on Windows, causing asset 404s and a blank screen.
   - *Resolution*: Configured `base: './'` in `frontend/vite.config.ts` and rebuilt distribution.
2. **Cold Start Latency Perception**:
   - *Problem*: Cold model loading (ViT + Wav2Vec2 + Whisper) requires ~8 seconds on initial launch.
   - *Resolution*: Added an immediate responsive CSS-animated splash screen in `desktop/main.js` that displays loading progress while polling `/api/health`, transitioning smoothly to the live dashboard as soon as the core is ready.
3. **Windows GUI Process Stdio Crash (`0xC000013A`)**:
   - *Problem*: In Windows GUI applications, `stdio: 'inherit'` inherits NULL standard handles, causing Python to terminate immediately when writing logs.
   - *Resolution*: Configured piped stdio (`['ignore', 'pipe', 'pipe']`) with real-time log forwarding to terminal stdout and targeted Python 3.11 executable path resolution.

### C. Live Desktop State
- App process actively running with WebSocket event stream open on `ws://127.0.0.1:8765/api/ws`.
- All dashboard views operational: Live Monitoring, Media Analysis, Alert History, Models & Speed, Privacy Retention, and Licenses.


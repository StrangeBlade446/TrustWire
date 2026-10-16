# Trustwire System Architecture

## Overview

Trustwire is architected as an autonomous, multi-layered Windows desktop application. The system divides responsibilities between a lightweight, modern React desktop frontend and a high-performance, asynchronous Python backend core.

```
+-------------------------------------------------------------------------+
|                         Trustwire Desktop Application                   |
|                                                                         |
|  +-----------------------------------+   +---------------------------+  |
|  |     Electron Desktop Shell        |   |    React 18 + TypeScript  |  |
|  | - Window Lifecycle & Native Frame |<->| - Dark Graphite UI        |  |
|  | - Subprocess & Health Monitoring  |   | - 7 Dedicated Views       |  |
|  +-----------------------------------+   +---------------------------+  |
|                                                        ^                |
|                                                        | HTTP/WS API    |
+--------------------------------------------------------|----------------+
                                                         v
+-------------------------------------------------------------------------+
|                  Localhost Backend Core (127.0.0.1:8765)                |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |   FastAPI Service Layer & Capability Token Authentication         |  |
|  +-------------------------------------------------------------------+  |
|           |                           |                     |           |
|           v                           v                     v           |
|  +------------------+     +--------------------+   +-----------------+  |
|  | Video Deepfakes  |     | Audio Anti-Spoof   |   | Speech & Fraud  |  |
|  | - OpenCV Haar    |     | - PyAV Resampler   |   | - Faster-Whisper|  |
|  | - ViT Classifier |     | - Wav2Vec2 Model   |   | - Fraud Rules   |  |
|  | - ONNX Runtime   |     | - PyTorch CPU      |   | - Negation/Quo  |  |
|  +------------------+     +--------------------+   +-----------------+  |
|           ^                           ^                     ^           |
|           |                           |                     |           |
|  +-------------------------------------------------------------------+  |
|  |   Live Capture Engine: Windows WASAPI Loopback + mss Screen Grab  |  |
|  |   Bounded Ring Buffers • Zero Latency Frame-Dropping • No Disk IO |  |
|  +-------------------------------------------------------------------+  |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |   Privacy & Retention Manager (15-Minute Expiry & Auto-Purge)     |  |
|  |   Central Alert Hub & Cooldown Throttle Engine                    |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

## Key Components

### 1. Electron Desktop Shell (`desktop/`)
- Launches the local Python backend via child process.
- Verifies backend readiness by polling `/api/health`.
- Creates a secure, context-isolated browser window loading `frontend/dist/index.html`.
- Implements process cleanup (`taskkill` on Windows) on shutdown to ensure zero orphaned background processes.

### 2. Frontend Interface (`frontend/`)
- Built with React 18, TypeScript, Vite, and Tailwind CSS.
- Screens:
  - **Dashboard:** Telemetry overview, model status pills, active alerts feed.
  - **Live Monitoring:** Real-time toggles for video, audio, and fraud channels; monitor selector; WASAPI speaker selector.
  - **Analyse Media:** Drag-and-drop file inspector with separate tracks and timeline evidence.
  - **Alert History:** Filterable metadata audit log with acknowledge/dismiss actions.
  - **Models & Performance:** Detailed provenance, licenses, measured latencies, and limitations for each model.
  - **Privacy & Settings:** 15-minute retention countdown, active file counts, purge triggers, capability token configuration.
  - **About:** Attributions, license details, and vulnerability disclosure policy.

### 3. Localhost API Server (`backend/app.py`)
- FastAPI service bound strictly to `127.0.0.1:8765`.
- Requires an `X-Trustwire-Token` capability token to protect against unauthorized local access.
- Exposes bidirectional WebSockets (`/api/ws`) for instant alert push notifications and telemetry broadcasts.

### 4. Forensic Detection Engines
- **Video Deepfake Detector (`backend/detectors/video/`):**
  - OpenCV Haar Cascade extracts face bounding boxes.
  - Resizes to 224x224 RGB with `[-1.0, 1.0]` normalization.
  - Vision Transformer (ViT) quantized ONNX model runs on CPU in ~205ms.
  - Percentile aggregation computes whole-video classifications and timestamps.
- **Audio Deepfake Detector (`backend/detectors/audio/`):**
  - PyAV decodes and resamples audio to 16kHz mono float32.
  - Bounded 3.0-second sliding windows with 1.5-second stride.
  - Wav2Vec2 sequence classifier evaluates neural vocoder anomalies in ~287ms.
  - Returns suspicious continuous time intervals `[start_sec, end_sec]`.
- **Financial Fraud Rules Engine (`backend/fraud/`):**
  - Faster-Whisper transcribes spoken words using offline int8 quantized models.
  - Contextual regex and proximity evaluator flags combinations of credential theft, urgency coercion, remote-access extortion, and payment lures.
  - Negation and educational filters suppress false alarms on security warnings or educational tutorials.

### 5. Privacy & Retention Subsystem (`backend/privacy/`)
- Hard maximum retention of 15 minutes (900 seconds).
- Background cleaner runs every 30 seconds.
- Startup crash recovery scrubs leftover files from prior unexpected terminations.

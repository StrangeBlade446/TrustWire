# Trustwire — Executive Project Overview & Architectural Mission

> **Version:** 1.0.0  
> **Classification:** Technical Mastery & Project Defence Documentation  
> **Environment:** Windows 10/11 (x86_64), Python 3.11+, React 18 / Electron  
> **Security Posture:** 100% Air-Gapped / On-Device Local Inference  

---

## 1. Executive Summary

**Trustwire** is an open-source, client-side, zero-telemetry deepfake detection and synthetic media forensic workstation engineered specifically for Windows desktop environments. In an era where generative adversarial networks (GANs), diffusion architectures, and neural vocoders enable malicious actors to synthesize photorealistic video streams and clone human voices in real time, Trustwire serves as an autonomous, privacy-first defensive barrier.

Unlike enterprise solutions that require routing sensitive audio/video streams to cloud-hosted APIs—introducing severe privacy hazards, latency bottlenecks, and regulatory liabilities (e.g., GDPR, HIPAA)—Trustwire runs **100% locally on the user's host machine**. It pairs an asynchronous FastAPI backend running optimized ONNX Runtime and PyTorch pipelines with an Electron-based desktop shell and React 18 interface.

Trustwire operates across two distinct operational modes:
1. **Targeted Forensic Media Analysis:** Static, multi-modal ingestion of user-uploaded video (`.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`) and audio (`.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.aac`) files, providing temporal heatmaps, frame-by-frame face crops, vocoder speech anomaly scores, and container hardware tag audits.
2. **Real-Time Live Desktop Monitoring:** Non-intrusive background surveillance of active communications (Zoom, Microsoft Teams, Google Meet, Web browsers) utilizing ultra-fast Windows GDI/DirectX desktop frame grabs (`mss`) and WASAPI audio loopback streaming (`soundcard`), dispatching instant disparity warnings when synthetic manipulation exceeds calibrated thresholds.

```
+-------------------------------------------------------------------------------+
|                             TRUSTWIRE RUNTIME                                 |
|                                                                               |
|  +--------------------+        Local IPC / WS        +---------------------+  |
|  |  Electron / React  | <==========================> |   FastAPI Backend   |  |
|  | Desktop UI Layer   |                              |  Port 8765 Loopback |  |
|  +--------------------+                              +---------------------+  |
|            |                                                    |             |
|            | Floating Controls                                  |             |
|            v                                                    v             |
|  +--------------------+      GDI / WASAPI Capture    +---------------------+  |
|  | Native UI Overlay  | <--------------------------- |  MSS & Soundcard    |  |
|  |  (Controls / HUD)  |                              |  Loopback Drivers   |  |
|  +--------------------+                              +---------------------+  |
|                                                                 |             |
|                                                                 v             |
|                                                      +---------------------+  |
|                                                      | Dual Neural Core    |  |
|                                                      | ViT + Wav2Vec2      |  |
|                                                      +---------------------+  |
+-------------------------------------------------------------------------------+
```

---

## 2. Core Architectural Philosophy

### A. Strict Local Inference (Zero External Telemetry)
Trustwire rejects the cloud paradigm for security-critical forensic tasks. No video frame, audio buffer, facial crop, or transcript ever crosses a network boundary. All model weights reside on local disk (`models/`), and the FastAPI server binds exclusively to `127.0.0.1:8765`, guarded by an ephemeral, session-scoped cryptographic capability token (`TRUSTWIRE_API_TOKEN`).

### B. Dual-Vector Multi-Modal Verification
Deepfakes rarely exhibit uniform perfection across both visual and acoustic dimensions. Attackers frequently combine real video with cloned audio (audio dubbing) or real audio with face-swapped video (lip-sync / deepfake puppet). Trustwire implements independent, parallel neural pipelines:
- **Spatial Face Classification:** Vision Transformer (`prithivMLmods/deepfake-detector-model-v1` via ONNX Runtime) with dual Haar-cascade extraction and YCrCb chrominance skin filtering.
- **Temporal Speech Representation:** Wav2Vec2 (`MelodyMachine/Deepfake-audio-detection-V2` via PyTorch) processing raw 16kHz waveforms through convolutional feature encoders and transformer context layers.

### C. Provable Privacy Retention (15-Minute Rolling Ceiling)
To satisfy stringent corporate and legal retention standards, Trustwire features an automated `RetentionManager`. Temporary artifacts created during media ingestion or live monitoring chunks are stamped with Unix epoch timestamps. A background daemon executes garbage collection every 30 seconds, strictly purging any media artifact whose age exceeds **900 seconds (15 minutes)**. The host storage footprint is ephemeral and non-recoverable upon session teardown.

---

## 3. High-Impact Elevator Pitches

### 30-Second Pitch (Executive / Investor)
> *"Deepfakes have weaponized digital communications, costing organizations hundreds of millions in CEO voice fraud and virtual interview impersonation. Trustwire is an open-source, local-first Windows application that instantly detects synthetic video and cloned audio in real time. Because Trustwire runs entirely on-device without cloud servers, corporate meetings, private calls, and sensitive media remain completely private. We provide instant disparity alerts before the fraud succeeds."*

### 2-Minute Pitch (Technical Committee / Academic Evaluators)
> *"Modern generative pipelines—such as diffusion-based head reenactment, neural audio vocoders, and transformer-based TTS—exploit human perceptual biases. Trustwire counters this by deploying multi-modal neural feature extraction directly onto the client endpoint.*
>
> *On the video stream, Trustwire leverages high-performance Windows GDI capture downsampled to 1.0 fps. Candidate faces are detected via dual cascaded Haar classifiers with YCrCb color-space chrominance boundary verification, eliminating non-human false positives. Extracted 224x224 normalized face crops are fed to a fine-tuned Vision Transformer running in ONNX Runtime, generating spatial patch embeddings that capture high-frequency GAN boundaries and boundary blending artifacts. Simultaneously, Google SynthID watermark detection is performed via multi-scale edge correlation.*
>
> *On the audio stream, WASAPI loopback captures live system output at 16kHz mono. An RMS energy gate filters silence, routing valid phoneme windows into a Wav2Vec2 12-layer convolutional and transformer encoder. The model evaluates latent acoustic features, identifying vocoder phase inconsistencies and unnatural pitch harmonics.*
>
> *The entire system communicates via an internal WebSocket event hub to a lightweight React/Electron dashboard, maintaining full privacy via a hard 15-minute rolling retention manager with zero cloud egress."*

### 5-Minute Pitch (Comprehensive Defence Walkthrough)
> *(Detailed in `13_PRESENTATION_SCRIPT.md`)*

---

## 4. Problem Statement & Threat Vector Landscape

| Threat Vector | Real-World Attack Scenario | Trustwire Countermeasure |
| :--- | :--- | :--- |
| **Virtual Meeting Face Swapping** | Attacker joins a Zoom/Teams corporate board meeting using DeepFaceLive / SimSwap to impersonate a C-level executive. | Multi-scale face extraction + Vision Transformer ONNX classification detecting edge blending and facial boundary artifacts. |
| **Voice Cloning / CEO Fraud** | Criminal calls finance team using ElevenLabs / VALL-E zero-shot voice clone requesting an immediate wire transfer. | WASAPI loopback capture + Wav2Vec2 neural vocoder detection flagging synthetic harmonic distributions. |
| **Generative Video Watermark Evasion** | Disinformation campaigns distribute synthetic video generated via Gemini/Veo with invisible or altered digital watermarks. | Multi-scale SynthID sparkle edge template correlation searching for structural watermark signatures. |
| **Data Leakage via Cloud Forensic Tools** | User uploads confidential internal video to an online detection website, exposing proprietary data to third parties. | 100% client-side execution; network access restricted to local loopback (`127.0.0.1`). |
| **Persistent Disk Snooping** | Forensic tools cache analyzed surveillance video permanently on disk, creating a compliance and privacy liability. | Autonomous `RetentionManager` with a 900-second strict lifespan, startup orphan sweeping, and instant manual memory wipe. |

---

## 5. Scope Boundaries: Capabilities vs Limitations

To maintain uncompromising academic and engineering integrity during technical defence, Trustwire's boundaries are explicitly defined:

### What Trustwire DOES:
1. **Detects Facial Manipulation Artifacts:** Identifies GAN-generated faces, boundary seams, color inconsistencies, and neural synthesis patterns in localized face crops.
2. **Detects Synthetic Audio Vocoding:** Identifies artificial phase irregularities, robotic spectral envelopes, and vocoder signatures characteristic of modern TTS and voice conversion.
3. **Monitors Live Desktop Display & System Audio:** Captures any video player or conference app on screen and any sound emitted through the default Windows audio output device.
4. **Enforces Strict Ephemeral Retention:** Guarantees that ingested media files and debug frames are irreversibly removed within 15 minutes of creation.

### What Trustwire DOES NOT Do (Explicit Non-Goals):
1. **Biometric Speaker Identification:** Trustwire does *not* confirm whether an audio stream belongs to "John Doe"; it determines whether the speech is *human-organic* or *algorithmically synthesized*.
2. **Global Deepfake Guarantee:** No probabilistic detector can claim 100% accuracy. Low-resolution video (<64px face size), extreme compression artifacts (h.264 CRF > 35), or heavy acoustic background noise can yield indeterminate scores.
3. **Kernel-Level Call Interception:** Trustwire does not hook Windows kernel drivers or inject DLLs into third-party processes (e.g., Zoom.exe). It observes outputs via standard Windows APIs (GDI/WASAPI).
4. **DRM / Protected Content Decryption:** Trustwire respects Windows HDCP and protected media paths; DRM-protected streams (e.g., Netflix) will present black frames to the capture engine.

# Changelog — Trustwire

All notable changes to Trustwire are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-16

### Added
- **Deepfake Video Detection Engine:** Integrated real Vision Transformer (ViT) FaceForensics++ classifier via ONNX Runtime with Haar Cascade face detection, temporal frame sampling, and percentile aggregation.
- **Deepfake Audio & Synthetic Voice Detection:** Integrated real Wav2Vec2 audio classification checkpoint with 16kHz mono resampling, sliding-window chunking, and timestamped suspicious range detection.
- **Context-Aware Financial Fraud Rules Engine:** Rule taxonomy covering credential theft (OTP, PIN, passwords), urgency threats, remote-access coercion, and payment traps, with negation and educational context filters.
- **Offline Speech-to-Text Transcription:** Faster-Whisper (CTranslate2) int8 quantized Whisper engine for private local speech transcription.
- **Windows Live Monitoring Core:** Native screen capture via `mss` and system playback audio capture via `soundcard` Windows WASAPI loopback, with bounded queues to eliminate latency.
- **15-Minute Privacy Retention Policy:** Background cleaner, startup recovery on crashes, and explicit storage purge guaranteeing ephemeral media lifetime.
- **Desktop Interface:** React 18, TypeScript, Tailwind CSS, Lucide icons, and Electron desktop shell with capability token authentication.
- **Automated Test Suite:** Comprehensive test suite with 22 automated tests covering fraud rules, privacy retention, model smoke tests, and FastAPI REST/WebSocket endpoints.

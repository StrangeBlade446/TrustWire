# Trustwire Models and Third-Party Licenses Inventory

All models and third-party dependencies used in Trustwire are documented below with their licenses, provenance, execution hardware, and forensic boundaries.

## 1. Deep Learning Models

| Component | Architecture | Source / Provenance | License | Execution Engine | Size | Measured Runtime |
|-----------|--------------|---------------------|---------|------------------|------|------------------|
| **Video Deepfake Detection** | Vision Transformer (ViT) Image Classifier | `onnx-community/deepfake_vs_real_image_detection-ONNX` (dima806/deepfake_vs_real_image_detection) | Apache-2.0 | ONNX Runtime (CPU) | 83.3 MB (quantized) | 205 ms / frame |
| **Audio Deepfake Detection** | Wav2Vec2 Sequence Classifier | `MelodyMachine/Deepfake-audio-detection-V2` (Trained on ASVspoof benchmarks) | MIT | PyTorch / Transformers (CPU) | 360.7 MB | 287 ms / chunk |
| **Speech Transcription** | Whisper (tiny.en / tiny) | OpenAI / Systran `faster-whisper` | MIT | CTranslate2 (CPU int8) | 75 MB | 1140 ms / chunk |
| **Fraud & Social Engineering** | Context-Aware Multi-Vector Rules Engine | Trustwire Native Forensic Taxonomy | MIT | Python Regex & Logic | < 1 MB | 0.5 ms / sentence |

## 2. Model Decision Boundaries & Honest Limitations

### Video Deepfake Detection (ViT)
- **Input Pipeline:** 224x224 RGB cropped face, normalized to `[-1.0, 1.0]`.
- **Strengths:** Detects blending artifacts, frequency inconsistencies, and facial boundary discontinuities characteristic of FaceForensics++ deepfakes.
- **Limitations:** Does not perform 3D temporal continuity analysis across long sequences. Extremely low resolution (< 60px faces), severe compression, or heavy motion blur may produce inconclusive scores.

### Audio Deepfake Detection (Wav2Vec2)
- **Input Pipeline:** 16kHz mono audio chunk (1.0s to 3.0s window).
- **Strengths:** Discriminates high-frequency phase and spectral artifacts introduced by neural vocoders (HiFi-GAN, WaveGlow, Tacotron).
- **Limitations:** Evaluates acoustic synthetic characteristics only. Does not verify speaker biometric identity. Background stadium noise or microphone clipping may introduce ambiguity.

### Financial Fraud Detection
- **Input Pipeline:** Spoken words decoded by local Faster-Whisper.
- **Strengths:** Detects dangerous multi-vector extortion (e.g. credential theft + urgency, or remote desktop + bank login), while suppressing negated advice ("never share your OTP") and educational context.
- **Limitations:** Dependent on transcription accuracy. Does not access user bank accounts or block external financial transactions.

## 3. Third-Party Libraries

- **FastAPI / Starlette / Pydantic:** MIT License
- **ONNX Runtime:** MIT License
- **PyTorch & Torchaudio:** BSD-3-Clause
- **HuggingFace Transformers:** Apache-2.0
- **Faster-Whisper & CTranslate2:** MIT License
- **OpenCV (opencv-python-headless):** Apache-2.0
- **Soundcard:** BSD-3-Clause
- **mss:** MIT License
- **React & React-DOM:** MIT License
- **Electron:** MIT License
- **Tailwind CSS & Lucide React:** MIT License

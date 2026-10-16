# Security Policy — Trustwire

## Threat Model & Security Posture

Trustwire is designed as a privacy-first, local-only Windows desktop application. Our security architecture adheres to the following principles:

1. **Zero Remote Transmission:**
   All machine-learning inference (Vision Transformer, Wav2Vec2, Faster-Whisper, and the Contextual Fraud Engine) executes locally on your hardware. No media buffers, audio streams, video frames, or transcripts are sent to third-party cloud servers.

2. **Strict 15-Minute Maximum Retention:**
   Temporary diagnostic media files have a hardcoded 15-minute lifespan enforced by background schedulers and startup crash-recovery cleaners. Raw audio and video buffers are processed in memory and never persisted into application logs, alert history, or telemetry.

3. **Localhost Capability Token Authentication:**
   The communication channel between the React/Electron desktop shell and the FastAPI local core (`127.0.0.1:8765`) requires a cryptographically random capability token (`X-Trustwire-Token`). This prevents malicious websites or unauthorized local processes from issuing requests to the Trustwire API.

4. **Input Sanitization & Safe Decoding:**
   Uploaded media files are given sanitized UUID filenames to prevent path traversal attacks. Media parsing is bounded to supported formats (MP4, MKV, WebM, WAV, MP3, FLAC) with size limits (maximum 500MB).

5. **No Dangerous Shell Invocations:**
   The system never passes user-supplied inputs to shell command interpolations.

## Known Limitations

- **Probabilistic Forensics:** Machine learning models detect statistical anomalies and synthetic vocoder artifacts. They are probabilistic and should never be used as sole legal proof of identity or criminality.
- **Hardware Storage Limits:** While Trustwire actively purges temporary files after 15 minutes, standard operating-system file deletion does not guarantee forensic sanitization from SSD wear-leveling layers or filesystem journals.

## Reporting a Vulnerability

We appreciate responsible disclosure. If you discover a security vulnerability in Trustwire:

1. **Do not create a public GitHub issue.**
2. Send an email with a detailed technical description and reproducible proof-of-concept to: `security@trustwire.local` (or open a confidential GitHub Security Advisory).
3. Include information on the affected component (`backend`, `desktop`, `capture`, or `detectors`).
4. We will acknowledge receipt within 48 hours and work with you on a coordinated patch and release timeline.

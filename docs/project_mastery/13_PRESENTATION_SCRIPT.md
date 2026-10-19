# Trustwire — Complete Presentation Slide Deck & Verbal Defence Script

> **Setting:** Technical Project Defence / Academic Committee Review  
> **Target Audience:** Professors, Senior AI Researchers, and Cybersecurity Evaluators  
> **Tone:** Rigorous, Grounded, Authoritative, and Technically Precise  

---

## Slide 1: Title & Architectural Mission

### Visual Layout
- **Header:** Trustwire: On-Device Multi-Modal Deepfake Forensic Workstation
- **Subheader:** Real-Time Client-Side Synthetic Media Detection for Windows
- **Visual:** High-contrast schematic showing dual neural core (ViT + Wav2Vec2) running inside a Windows endpoint boundary, completely disconnected from external cloud servers.
- **Presenter Bio:** [Your Name], Lead AI Systems Architect & Forensic Researcher

### Spoken Script (Word-for-Word)
> *"Respected members of the evaluation committee, good morning. Today, I am proud to present **Trustwire**, an open-source, client-side forensic workstation engineered to detect deepfake video and synthetic audio in real time directly on Windows endpoints.*
>
> *Over the past two years, generative AI has crossed a dangerous threshold. Tools like diffusion head reenactment, zero-shot voice cloning, and neural vocoders allow malicious actors to impersonate trusted individuals across live video calls and audio communications. Trustwire was built to serve as an autonomous, privacy-preserving defensive barrier that verifies digital media authenticity without sacrificing user confidentiality."*

---

## Slide 2: The Defensive Dilemma: Why Cloud Detection Fails

### Visual Layout
- **Left Column (Cloud Approach):** Flowchart showing user video streaming to external cloud server $\rightarrow$ latency spike ($>2500$ ms) $\rightarrow$ GDPR/HIPAA privacy violations $\rightarrow$ third-party breach risk.
- **Right Column (Trustwire Approach):** Local GDI/WASAPI loopback $\rightarrow$ on-device SIMD neural inference $\rightarrow$ sub-second response ($<250$ ms) $\rightarrow$ zero network egress.

### Spoken Script
> *"When organizations look for deepfake detection solutions, they invariably encounter a fundamental dilemma: cloud-based detection APIs. Sending live boardroom video, confidential customer calls, or private voice memos to a third-party cloud server introduces severe regulatory and security risks under GDPR and HIPAA. Furthermore, cloud round-trip latencies exceed two to three seconds, rendering real-time intervention during live fraud impossible.*
>
> *Trustwire resolves this dilemma through a strict **zero-telemetry, on-device architecture**. Every frame grab, audio buffer, face crop, and neural inference operation executes 100% locally on the host machine using SIMD-accelerated CPU kernels, binding strictly to localhost loopback."*

---

## Slide 3: End-to-End System Architecture

### Visual Layout
- Full-screen architectural diagram from `02_SYSTEM_ARCHITECTURE.md`: Electron Main $\rightarrow$ FastAPI Backend (port 8765) $\rightarrow$ Screen Capture Worker (MSS GDI) $\rightarrow$ Audio Loopback Worker (WASAPI) $\rightarrow$ Dual Neural Core $\rightarrow$ Thread-Safe Alert Hub $\rightarrow$ WebSocket Broadcast $\rightarrow$ Native Windows Toast.

### Spoken Script
> *"Let us trace the architectural topology of Trustwire. The application is bifurcated into a high-performance presentation tier built with Electron and React 18, and a native asynchronous computational core powered by FastAPI and Python 3.11.*
>
> *Communication is mediated by an ephemeral cryptographic capability token generated at boot. During live monitoring, our background workers capture the desktop screen via Windows GDI BitBlt at 1.0 fps and intercept playback audio using WASAPI loopback streams. Captured buffers are pushed into bounded FIFO queues with automatic frame-dropping to guarantee zero latency drift. These streams feed our dual neural detection pipelines."*

---

## 4. Acoustic Forensics: Wav2Vec2 & Neural Vocoder Detection

### Visual Layout
- Diagram of Wav2Vec 2.0: Raw 16kHz waveform $\rightarrow$ 7-layer temporal 1D convolutional feature encoder (stride 320) $\rightarrow$ 12-layer Transformer self-attention blocks $\rightarrow$ mean temporal pooling $\rightarrow$ linear classification head $\rightarrow$ Softmax posterior probability.
- Audio silence gate formula: $E_{\text{RMS}} = \sqrt{\frac{1}{N}\sum x[n]^2} \ge 0.008$.

### Spoken Script
> *"In the audio domain, traditional approaches convert sound into Mel spectrograms and apply image classifiers. However, spectrograms discard acoustic phase information—precisely where modern neural vocoders leave their most telling manipulation footprints.*
>
> *Trustwire utilizes a fine-tuned **Wav2Vec 2.0** sequence classifier processing raw, uncompressed 16kHz waveforms directly. The architecture utilizes a 7-layer temporal convolutional encoder that downsamples the audio by a factor of 320 into 512-dimensional latent representations, followed by 12 multi-head self-attention transformer blocks.*
>
> *To eliminate false alarms during conversational pauses, we implement an algorithmic acoustic silence gate: any chunk with RMS energy below 0.008 is automatically bypassed. Chunks with active speech are evaluated, and multi-chunk temporal voting determines whether vocoder phase artifacts and unnatural pitch regularities warrant a synthetic media alert."*

---

## Slide 5: Visual Forensics: Vision Transformer Face Classification

### Visual Layout
- Visual pipeline: 1080p frame $\rightarrow$ Dual Haar Cascades $\rightarrow$ YCrCb skin chrominance filter ($Cr \in [133, 173], Cb \in [77, 127]$) $\rightarrow$ 224x224 RGB crop $\rightarrow$ ViT-Base/16 (196 patches of 16x16) $\rightarrow$ Class token [CLS] classification.

### Spoken Script
> *"In the visual domain, Trustwire deploys a localized forensic pipeline rather than processing full uncropped frames. Deepfake manipulation artifacts—such as boundary blending seams, color disparity, and GAN checkerboard noise—are localized around the human face.*
>
> *We first locate faces using dual cascaded Haar classifiers. To prevent background objects from causing false positives, we apply a YCrCb chrominance skin-tone filter: any candidate bounding box lacking human skin chrominance is instantly rejected.*
>
> *The valid face crop is resized to 224x224 and fed to a fine-tuned **Vision Transformer** in ONNX Runtime. The ViT divides the face into 196 discrete patches and computes global pairwise self-attention across all patches simultaneously. This enables the model to spot structural discrepancies between distant facial landmarks—such as mismatched corneal specular reflections or jawline blending artifacts."*

---

## Slide 6: Multi-Scale Watermark & Container Forensics

### Visual Layout
- Left: Google SynthID 4-pointed sparkle template and multi-scale Canny edge correlation matching diagram ($R \ge 0.55$).
- Right: PyAV container metadata table comparing camera hardware tags (`Apple iPhone`) vs software synthesizers (`Lavf`, `FFmpeg`).

### Spoken Script
> *"In addition to deep neural networks, Trustwire introduces secondary forensic verification vectors. With the rise of model watermarking by Google and other providers, we have integrated a multi-scale template correlation engine that scans frames for the Google SynthID sparkle watermark across scales from 0.40 to 1.15 using Canny edge filtering.*
>
> *Furthermore, during static media analysis, PyAV inspects container metadata. Authentic camera recordings contain hardware EXIF tags detailing camera model, lens aperture, and capture device. Algorithmic deepfakes and screen captures almost exclusively originate from software encoders like Libavformat. This metadata audit provides valuable corroborating evidence for forensic reports."*

---

## Slide 7: Context-Aware Financial Scam Engine

### Visual Layout
- Mathematical compounding formula:
  $$S = \min\left(1.0, \; \frac{\sum w_i}{100.0} \cdot (1.0 + 0.30 \cdot (C - 1))\right)$$
- Diagram showing Whisper transcription feeding into the 7-category taxonomy with 50-character negation windowing and 60% educational PSA dampening.

### Spoken Script
> *"Deepfakes in the wild are primarily financial weapons. Criminals pair cloned voices with social engineering playbooks. Trustwire addresses this by incorporating an integrated Financial Scam Risk Engine.*
>
> *Using local Faster-Whisper automatic speech recognition, spoken utterances are transcribed and evaluated against a taxonomy of seven distinct fraud categories—including urgent action, credential theft, and authority impersonation.*
>
> *Critically, we avoid naive keyword counting. Our engine applies a **multi-category compounding multiplier**: when threats span multiple distinct categories, the risk score compounds exponentially. Simultaneously, a 50-character negation window prevents false alarms on phrases like 'never share your password', and educational keyword detection dampens scores during cybersecurity training."*

---

## Slide 8: The 15-Minute Rolling Privacy Buffer

### Visual Layout
- State diagram of `RetentionManager` showing artifact creation $\rightarrow$ epoch timestamping $\rightarrow$ 30-second garbage collection loop $\rightarrow$ 900-second strict expiration deletion $\rightarrow$ startup orphan sweep.

### Spoken Script
> *"A cornerstone of Trustwire's engineering ethics is our **15-Minute Rolling Privacy Buffer**. To ensure that Trustwire cannot be misused as persistent surveillance software, the application enforces a strict 900-second hard ceiling on disk retention.*
>
> *Every temporary file created during upload or live capture is registered with an epoch timestamp. An autonomous background daemon executes garbage collection every 30 seconds, unlinking any file older than 15 minutes. On application boot, an orphan sweep purges any files stranded by previous unclean shutdowns, and users can trigger an instant manual wipe with a single click."*

---

## Slide 9: Performance Optimization & Hardware Efficiency

### Visual Layout
- Benchmark table: Video pipeline latency (238 ms), Audio pipeline latency (287 ms), Total RAM working set (~1.0 GB).
- Big-O complexity comparison: Fixed ViT patch attention $\mathcal{O}(N^2 d)$ where $N=196$ vs variable length LLMs.

### Spoken Script
> *"To ensure Trustwire runs seamlessly on standard business laptops without requiring high-end dedicated GPUs, we focused heavily on algorithmic efficiency.*
>
> *By decoupling capture and inference into asynchronous threads with bounded queues, our live video pipeline completes within 238 milliseconds per frame, operating comfortably within our 1.0 fps sampling budget. Total RAM consumption remains capped at approximately 1.0 gigabyte across both neural models, the backend server, and the Electron frontend.*
>
> *Our test suite of 22 automated tests passes with 100% reliability, validating everything from REST lifecycle endpoints to silence gating and skin-tone chrominance filtering."*

---

## Slide 10: Conclusion & Project Defence Summary

### Visual Layout
- Summary bullet points:
  - 100% Client-Side Local Inference (Zero Network Telemetry)
  - Dual-Vector Neural Architecture (ViT + Wav2Vec2)
  - Multimodal Forensic Corroboration (SynthID + Container Hardware Tags)
  - Semantic Scam Risk Compounding (Whisper + Regex Taxonomy)
  - Provable Ephemeral Retention (900-Second Rolling Ceiling)
- Q&A Invitation Banner.

### Spoken Script
> *"In summary, Trustwire demonstrates that effective, state-of-the-art deepfake detection does not require compromising user privacy or relying on centralized cloud infrastructure. By combining Vision Transformers, Wav2Vec2 speech representations, container metadata auditing, and contextual scam heuristics inside an ephemeral privacy buffer, Trustwire provides an autonomous, verifiable defense against synthetic deception.*
>
> *Thank you for your time and consideration. I look forward to your questions."*

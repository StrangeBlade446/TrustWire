# Trustwire — Forensic Glossary & Technical Learning Roadmap

> **Target:** Beginners to Advanced Engineers Mastering Deepfake Forensics & AI Systems  
> **Structure:** Technical Terminology Dictionary + 4-Phase Mastery Syllabus  

---

## 1. Comprehensive Technical Glossary

### A. Acoustic & Signal Processing Terminology

- **Anti-Aliasing Filter:** An analog or digital low-pass filter applied before downsampling to attenuate signal frequencies above the Nyquist frequency ($f_s / 2$), preventing spectral overlap.
- **ASVspoof:** The premier international academic challenge and benchmark dataset evaluating automatic speaker verification systems against synthetic speech and logical access voice cloning attacks.
- **Formants:** Resonant frequency peaks of the human vocal tract (labeled $F_1, F_2, F_3$) that distinguish specific vowels and phonemes.
- **Glottal Pulse:** The periodic puff of acoustic air emitted through the vibrating vocal folds during voiced phonation.
- **Jitter:** Cycle-to-cycle perturbations in the fundamental frequency ($F_0$) of a voice. Synthetic neural vocoders often produce unnaturally invariant jitter profiles.
- **Mel Scale:** A non-linear perceptual scale of pitches judged by human listeners to be equal in distance from one another:
  $$m = 2595 \log_{10}\left(1 + \frac{f}{700}\right)$$
- **Neural Vocoder:** A deep neural network (e.g. HiFi-GAN, WaveGlow) that synthesizes time-domain audio waveforms from acoustic representations such as Mel spectrograms.
- **Nyquist Frequency:** Exactly half of the sampling frequency ($f_s / 2$). The theoretical upper ceiling of reproducible frequency content.
- **RMS Energy (Root-Mean-Square):** A mathematical measure of signal power:
  $$E_{\text{RMS}} = \sqrt{\frac{1}{N}\sum_{n=1}^N x[n]^2}$$
- **Short-Time Fourier Transform (STFT):** A Fourier-related transform used to determine the sinusoidal frequency and phase content of local sections of a signal as it changes over time.

---

### B. Computer Vision & Visual Forensics Terminology

- **Canny Edge Detector:** A multi-stage edge detection algorithm utilizing Gaussian smoothing, gradient magnitude calculation, non-maximum suppression, and hysteresis thresholding ($T_{\text{low}}, T_{\text{high}}$).
- **Face Swap:** A generative manipulation technique replacing the face of an individual in a target video with the face of a source individual (e.g. DeepFaceLab, SimSwap).
- **Facial Reenactment:** Animating a source individual's facial expressions and gaze driven by the movements of a driving actor (e.g. LivePortrait, First Order Motion Model).
- **Haar Feature-Based Cascade:** An object detection algorithm where a cascade function is trained from positive and negative images, evaluating rectangular sums via integral images.
- **Normalized Cross-Correlation (NCC):** A template matching metric invariant to linear changes in image illumination, bounded strictly within $[-1.0, 1.0]$.
- **Patch Projection:** In Vision Transformers, partitioning a 2D image into non-overlapping grid patches (e.g. $16 \times 16$) and projecting them via a linear matrix into latent embedding space.
- **SynthID:** Digital watermarking technology developed by Google DeepMind embedding invisible, tamper-resistant identifiers into AI-generated audio, video, and images.
- **Vision Transformer (ViT):** An architecture that applies the Transformer encoder directly to sequences of flattened image patches, computing global pairwise self-attention without convolution.
- **YCrCb Color Space:** An encoding system representing color as luminance ($Y$) and two chrominance components: red-difference ($Cr$) and blue-difference ($Cb$).

---

### C. Systems, Concurrency & Machine Learning Terminology

- **AVX2 (Advanced Vector Extensions 2):** An x86 instruction set extension enabling 256-bit SIMD operations, allowing CPU cores to process 8 float32 numbers in a single clock cycle.
- **Capability Token:** An unguessable cryptographic token granting access to a specific API session, preventing unauthorized cross-origin requests.
- **Equal Error Rate (EER):** The point on a Detection Error Tradeoff (DET) curve where the False Acceptance Rate (FAR) equals the False Rejection Rate (FRR).
- **Logit:** The raw, unnormalized vector $\mathbf{z}$ output by the final linear layer of a neural network before Softmax activation.
- **Softmax Function:** An activation operator transforming a vector of $K$ real values into a probability distribution summing to 1.0:
  $$\text{Softmax}(\mathbf{z})_i = \frac{e^{z_i}}{\sum_{j=1}^K e^{z_j}}$$
- **WASAPI (Windows Audio Session API):** Low-level Microsoft Windows client API enabling applications to manage audio streams directly from audio endpoints in exclusive or loopback mode.

---

## 2. 4-Phase Mastery Learning Roadmap

```
[Phase 1: DSP & Vision Foundations] 
            │
            ▼
[Phase 2: Transformers & Deep Learning]
            │
            ▼
[Phase 3: Forensic Media Analysis & Attacks]
            │
            ▼
[Phase 4: Systems Engineering & Production Deployment]
```

### Phase 1: Signal Processing & Classical Computer Vision (Weeks 1–3)
- **Core Topics:** Sampling theory, Nyquist-Shannon limits, aliasing, discrete convolutions, STFT windowing, Mel filterbanks, color spaces (RGB vs YCrCb), Haar features, Canny edge detection.
- **Recommended Textbooks:**
  - *Discrete-Time Signal Processing* — Oppenheim & Schafer.
  - *Digital Image Processing* — Gonzalez & Woods.
- **Hands-On Lab:** Write a Python script using NumPy to calculate the STFT of a WAV file from scratch without using Librosa.

### Phase 2: Neural Networks & Transformer Architectures (Weeks 4–7)
- **Core Topics:** Convolutions, Backpropagation, Cross-Entropy Loss, Self-Attention mechanisms, Scaled Dot-Product Attention proof, Vision Transformers (ViT), Wav2Vec 2.0 self-supervised speech representations.
- **Foundational Papers:**
  - Vaswani et al. (2017): *"Attention Is All You Need"*.
  - Dosovitskiy et al. (2020): *"An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale"*.
  - Baevski et al. (2020): *"wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations"*.
- **Hands-On Lab:** Inspect `backend/detectors/video/detector.py` and trace how an image crop reshapes into `(1, 3, 224, 224)` and feeds into ONNX Runtime.

### Phase 3: Synthetic Media Forensics & Adversarial Attacks (Weeks 8–10)
- **Core Topics:** Generative Adversarial Networks (GANs), Diffusion Models (DDPM), Neural Vocoders, ASVspoof benchmarks, FaceForensics++, temporal artifact voting, digital watermarks (SynthID), adversarial evasion techniques (FGSM, noise injection).
- **Recommended Reading:**
  - Academic survey papers on Deepfake Video and Audio Detection (IEEE TPAMI / ACM Computing Surveys).
- **Hands-On Lab:** Run `tests/test_detectors.py` and modify the skin-tone chrominance thresholds to observe how false-positive rejection changes.

### Phase 4: Systems Engineering, Concurrency & Windows Security (Weeks 11–12)
- **Core Topics:** Python multi-threading vs multiprocessing, Global Interpreter Lock (GIL), bounded FIFO queues, Win32 API ctypes interop, Windows WASAPI audio loopback, Electron-to-backend IPC, GDPR data retention enforcement.
- **Hands-On Lab:** Trace the live capture pipeline in `backend/capture/manager.py` from the MSS screen grab to the WebSocket broadcast in `backend/alerts/hub.py`.

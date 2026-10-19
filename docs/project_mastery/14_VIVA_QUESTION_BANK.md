# Trustwire — Comprehensive Viva Voce & Technical Defence Question Bank (80+ Questions)

> **Target:** M.Tech / B.Tech / Ph.D. Viva Committees, AI Research Evaluators, Technical Judges  
> **Format:** Short Spoken Answer + Deep Technical Explanation + Code Reference + Examiner Trap Alert  

---

## Category 1: System Architecture & Concurrency (Q1 - Q6)

### Q1: Why did you decouple the application into an Electron frontend and a FastAPI backend instead of using pure Python (Tkinter/PyQt) or pure Electron?
- **Short Spoken Answer:** Decoupling cleanly isolates the UI rendering thread from heavy neural compute, ensuring 60 fps desktop responsiveness while retaining native Python C-extensions for PyTorch, ONNX, and PyAV.
- **Deep Technical Explanation:** A unified Python GUI (Tkinter or PyQt) suffers from Python's Global Interpreter Lock (GIL). Running multi-threaded neural inference alongside a GUI event loop frequently causes interface micro-stutters and window freezing on Windows. Conversely, running deep learning models inside Electron via ONNX.js lacks native AVX2 SIMD acceleration and hardware bindings. By separating them into an Electron/React Chromium process and a native FastAPI process communicating over local loopback (`127.0.0.1:8765`), we achieve native OS notifications and GPU-accelerated UI rendering while running C++ optimized inference in dedicated background threads.
- **Code Reference:** `desktop/main.js`, `backend/app.py`.
- **Examiner Trap:** *Do not say "Electron is faster than PyQt."* Electron uses more memory; the justification is architectural decoupling, superior WebSockets/modern React component ecosystem, and thread isolation.

### Q2: How does Trustwire ensure thread safety between the capture workers, inference pipeline, and WebSocket broadcast?
- **Short Spoken Answer:** We utilize bounded, thread-safe Python `queue.Queue` primitives for inter-thread media passing, and thread-safe coroutine scheduling via `asyncio.run_coroutine_threadsafe()` to cross from OS inference threads into the async event loop.
- **Deep Technical Explanation:** `ScreenCaptureWorker` and `AudioLoopbackWorker` run in independent OS threads (`threading.Thread`). They push frames into `frame_queue` and `audio_queue`. `queue.Queue` implements internal thread locking (`threading.Lock` and `Condition` variables), preventing race conditions during push and pop. When the inference worker in `backend/capture/manager.py` produces an alert, it calls `alert_hub.dispatch_alert()`. Because the FastAPI WebSocket server runs on an asyncio event loop in Thread 1, `alert_hub` uses `asyncio.run_coroutine_threadsafe(self.broadcast_alert(alert), self._loop)` to schedule the outbound WebSocket broadcast safely across the thread boundary without deadlocks.
- **Code Reference:** `backend/capture/manager.py`, `backend/alerts/hub.py`.

### Q3: What happens if the live inference pipeline cannot keep up with screen capture frame rates?
- **Short Spoken Answer:** Our frame queue has a bounded `maxsize=3`. When full, the capture worker immediately discards the oldest frame, preventing queue ballooning and ensuring latency never exceeds 1.1 seconds.
- **Deep Technical Explanation:** In naive implementations, unbounded queues accumulate backlogged frames when inference experiences transient CPU load spikes. This results in latency drift where an alert fires 30 seconds after the event occurred on screen. In `backend/capture/screen.py`, when `frame_queue.full()` is detected, `frame_queue.get_nowait()` evicts the stale frame before enqueuing the fresh capture. This guarantees that Trustwire always processes real-time data with bounded memory consumption.

### Q4: Why is FastAPI running on port 8765 rather than standard port 8000?
- **Short Spoken Answer:** Port 8000 is heavily contended by development tools, Docker containers, and local proxies. Using 8765 minimizes port collision on Windows workstations.
- **Code Reference:** `backend/config.py::settings.port`.

### Q5: What security mechanism prevents third-party local applications or browser tabs from abusing your local API?
- **Short Spoken Answer:** Trustwire requires an ephemeral cryptographic capability token (`TRUSTWIRE_API_TOKEN`) passed via the `X-Trustwire-Token` HTTP header on all REST routes and WebSocket handshakes.
- **Deep Technical Explanation:** Localhost APIs are vulnerable to Cross-Site Port Attacks (CSPA) and drive-by web requests where a malicious website in the user's browser attempts to issue `POST http://localhost:8765/api/...`. Trustwire defends against this by generating a session-scoped 32-character UUID4 token on startup. Electron injects this token into the React webview environment. Any request without a matching `X-Trustwire-Token` header receives an immediate `401 Unauthorized` response.
- **Code Reference:** `backend/app.py::verify_token()`, `backend/config.py`.

### Q6: Why did you eliminate the secondary floating overlay window in the latest version?
- **Short Spoken Answer:** Managing multiple separate BrowserWindow instances on Windows caused window-focus conflicts and unnecessary GPU compositor memory overhead. We streamlined controls into the primary dashboard and live toasts.
- **Code Reference:** `desktop/main.js`, `frontend/src/components/DisparityAlertPopup.tsx`.

---

## Category 2: Audio Deepfake Detection & Signal Processing (Q7 - Q14)

### Q7: Why use Wav2Vec2 on raw waveforms instead of a 2D CNN on Mel spectrograms?
- **Short Spoken Answer:** Mel spectrograms discard acoustic phase information, whereas Wav2Vec2's 1D convolutional feature encoder analyzes raw temporal sample sequences, preserving high-frequency vocoder phase anomalies.
- **Deep Technical Explanation:** Standard audio pipelines apply the Short-Time Fourier Transform (STFT), extract magnitude $|X(m, k)|$, and project onto the Mel filterbank, completely discarding the complex phase angle $\theta(m, k) = \arctan\left(\frac{\text{Im}(X)}{\text{Re}(X)}\right)$. However, generative neural vocoders (like HiFi-GAN or WaveGlow) synthesize speech by estimating phase, which leaves distinct mathematical artifacts (phase cancellation, dispersion, and boundary jitter) in the time domain. Wav2Vec2 operates directly on the 1D discrete sequence $x[n]$, capturing these phase irregularities.

### Q8: What is the sample rate required by Trustwire's audio detector, and why?
- **Short Spoken Answer:** 16,000 Hz mono float32. This matches the pretrained input contract of Wav2Vec 2.0, providing an 8,000 Hz Nyquist bandwidth covering all human speech formants.
- **Code Reference:** `backend/detectors/audio/detector.py::_decode_and_resample()`.

### Q9: Why is silence gating via Root-Mean-Square (RMS) energy essential?
- **Short Spoken Answer:** Deep neural classifiers hallucinate unpredictable, false-positive synthetic probabilities when fed silence or ambient room noise.
- **Deep Technical Explanation:** Wav2Vec2 was trained on human phonemes. During conversational silences, the input tensor contains only Gaussian thermal noise or microphone hum. Because the model enforces global temporal pooling, these low-amplitude noise fluctuations are normalized and projected through the classification head, producing erratic scores. Trustwire calculates $E_{\text{RMS}} = \sqrt{\frac{1}{N}\sum x[n]^2}$. Chunks with $E_{\text{RMS}} < 0.008$ are immediately bypassed, returning $P(\text{Fake}) = 0.0$.
- **Code Reference:** `backend/detectors/audio/detector.py::analyze_samples()`.

### Q10: What are the window and stride parameters used for audio segmentation?
- **Short Spoken Answer:** A 3.0-second analysis window (48,000 samples) with a 1.5-second stride (24,000 samples), providing 50% temporal overlap.
- **Deep Technical Explanation:** A 3.0-second window ensures sufficient phoneme context for the 12 Transformer self-attention layers. The 50% overlap guarantees that speech phonemes occurring near the edge of one window are centered in the subsequent window, preventing truncation artifacts.

### Q11: Explain your temporal audio aggregation logic.
- **Short Spoken Answer:** For short clips ($\le 3$ chunks), we require peak score $\ge 0.80$ and authentic ratio $< 0.60$. For longer recordings, we require suspicious ratio $\ge 0.40$ or median score $\ge 0.65$.
- **Code Reference:** `backend/detectors/audio/detector.py::analyze_audio()`.

### Q12: How does Trustwire downmix stereo audio to mono?
- **Short Spoken Answer:** By averaging left and right channels: $x_{\text{mono}}[n] = \frac{x_L[n] + x_R[n]}{2}$ using PyAV's native audio resampler.

### Q13: Can Trustwire detect who is speaking (speaker identification)?
- **Short Spoken Answer:** No. Trustwire detects *synthetic vocoder manipulation*, not biometric speaker identity.
- **Examiner Trap:** Never claim Trustwire verifies speaker identities. It verifies whether the speech was organically spoken or synthetically generated.

### Q14: What happens if an uploaded audio clip is shorter than 3.0 seconds?
- **Short Spoken Answer:** The 1D array is right-padded with zeros up to 48,000 samples before passing into the PyTorch tensor.

---

## Category 3: Video Deepfake Detection & Computer Vision (Q15 - Q22)

### Q15: Why did you choose a Vision Transformer (ViT) over an EfficientNet or ResNet backbone?
- **Short Spoken Answer:** ViT computes global pairwise self-attention across all image patches simultaneously, enabling it to detect long-range spatial inconsistencies such as mismatched corneal reflections and facial boundary blending seams.
- **Deep Technical Explanation:** Convolutional architectures possess strong inductive bias (locality and translation equivariance), which makes them efficient but biases them toward local texture statistics. In contrast, Vision Transformers partition the face into 196 non-overlapping patches ($16 \times 16$) and evaluate all patch interactions. This allows the network to learn structural correlations between distant facial regions—for instance, verifying whether the illumination on the left cheek matches the specular reflection on the right cornea.
- **Code Reference:** `backend/detectors/video/detector.py`.

### Q16: Why do you crop the face instead of analyzing the entire 1080p frame?
- **Short Spoken Answer:** Deepfake manipulation is localized on the face; analyzing the whole frame introduces background noise and wastes 95% of computational bandwidth on non-manipulated pixels.
- **Deep Technical Explanation:** If an entire 1920x1080 frame is resized directly to 224x224, a human face occupying 200x200 pixels is crushed down to less than 25x25 pixels, destroying high-frequency boundary artifacts. By cropping the bounding box with a 20% margin prior to resizing, the facial region retains maximum resolution.

### Q17: What is the purpose of the YCrCb skin-tone validation filter?
- **Short Spoken Answer:** Haar cascades frequently trigger false positives on complex background patterns. The YCrCb filter verifies human chrominance ($Cr \in [133, 173], Cb \in [77, 127]$) before invoking the neural network.
- **Deep Technical Explanation:** In OpenCV, Haar cascades evaluate rectangular intensity differences, often flagging shirt collars, wallpaper textures, or ceiling lights as faces. If an arbitrary object is fed into a fine-tuned deepfake classifier, the model produces uncalibrated garbage logits. In `detector.py`, Trustwire converts the crop to YCrCb. If skin pixels constitute $<15\%$ of the crop, it is immediately discarded.

### Q18: What is Google SynthID and how does Trustwire detect it?
- **Short Spoken Answer:** SynthID is a digital watermark embedded in generative media. Trustwire uses multi-scale normalized cross-correlation (scales 0.40 to 1.15) on Canny edge maps against a reference 4-pointed sparkle template.
- **Code Reference:** `backend/detectors/video/detector.py::_detect_synthid_watermark()`.

### Q19: What are the Canny edge detector thresholds used for SynthID matching?
- **Short Spoken Answer:** $T_{\text{low}} = 30$ and $T_{\text{high}} = 90$, designed to isolate faint watermark contours while suppressing background video noise.

### Q20: How does Trustwire inspect video container hardware tags?
- **Short Spoken Answer:** Using PyAV, it reads container metadata dictionaries for hardware tags (`make`, `model`, `lens`) versus software re-encoding flags (`Lavf`, `HandBrake`, `ffmpeg`).

### Q21: What is the temporal sampling rate for uploaded videos?
- **Short Spoken Answer:** 1.0 frame per second (1.0 fps). Deepfake artifacts persist across consecutive frames; sampling at 1 fps provides $>98\%$ detection coverage while reducing compute by $96.7\%$.

### Q22: What happens if a video contains no faces?
- **Short Spoken Answer:** Trustwire returns `Inconclusive` with $P=0.0$ and a clear message: *"No human faces detected in analyzed video frames."* It does not crash or generate false alarms.

---

## Category 4: Mathematics & Formal Derivations (Q23 - Q30)

### Q23: Why do we divide the attention dot product by $\sqrt{d_k}$ in Transformer self-attention?
- **Short Spoken Answer:** For large dimensions $d_k$, the variance of the dot product equals $d_k$. Dividing by $\sqrt{d_k}$ forces unit variance, preventing the Softmax function from saturating and causing vanishing gradients.
- **Mathematical Derivation:** *(See formal proof in `05_MATHEMATICS_AND_EQUATIONS.md` Section 4B)*.

### Q24: What is the difference between raw model logits and calibrated probabilities?
- **Short Spoken Answer:** Logits are unconstrained real-valued outputs $\mathbf{z} \in (-\infty, \infty)$. Softmax maps them to $[0, 1]$, but calibration requires temperature scaling or Platt scaling to ensure a score of 0.8 represents an 80% true empirical probability.

### Q25: Write the formula for the Root-Mean-Square (RMS) energy.
- **Answer:**
  $$E_{\text{RMS}} = \sqrt{\frac{1}{N}\sum_{n=1}^N x[n]^2}$$

### Q26: State the Nyquist-Shannon Sampling Theorem.
- **Answer:** A continuous bandlimited signal containing maximum frequency $B$ can be perfectly reconstructed from its samples if and only if the sampling frequency $f_s > 2B$.

### Q27: State the formula for the Mel frequency scale.
- **Answer:**
  $$m = 2595 \log_{10}\left(1 + \frac{f}{700}\right)$$

### Q28: How is the Normalized Cross-Correlation (NCC) score bounded?
- **Short Spoken Answer:** By the Cauchy-Schwarz inequality, $R(x, y) \in [-1.0, 1.0]$. A score of 1.0 represents a mathematically identical template match.

### Q29: Write the formula for the compounding fraud risk score in Trustwire.
- **Answer:**
  $$S = \min\left(1.0, \; \left(\frac{\sum w_i}{100.0}\right) \cdot (1.0 + 0.30 \cdot (C - 1))\right)$$

### Q30: What is the Equal Error Rate (EER)?
- **Short Spoken Answer:** The specific decision threshold at which the False Acceptance Rate (FAR) equals the False Rejection Rate (FRR). A lower EER indicates a superior forensic classifier.

---

## Category 5: Financial Scam Detection & NLP (Q31 - Q38)

### Q31: Why did you implement a compounding multiplier instead of simple keyword addition?
- **Short Spoken Answer:** Single keyword collisions occur frequently in benign speech. Compounding ensures risk escalates exponentially only when attacks cross multiple distinct social engineering categories.

### Q32: Name four of the seven fraud categories in Trustwire's rules taxonomy.
- **Answer:** `urgent_action`, `credential_theft`, `financial_coercion`, and `authority_impersonation`.
- **Code Reference:** `backend/fraud/rules.py`.

### Q33: How does Trustwire prevent false alarms on "Never share your password"?
- **Short Spoken Answer:** A 50-character negation window checks for preceding phrases like "never", "do not", or "protect your", discarding the match if negated.

### Q34: What is educational dampening?
- **Short Spoken Answer:** If educational or news keywords ("awareness", "cybersecurity training", "scam warning") appear in the transcript, the risk score is dampened by 60% ($S \times 0.40$).

### Q35: Which speech-to-text model is used, and what is its precision format?
- **Short Spoken Answer:** `faster-whisper` `tiny` model running in 8-bit integer quantization (INT8) on CPU via CTranslate2.

### Q36: At what score threshold does a fraud alert trigger as Critical?
- **Short Spoken Answer:** $S \ge 0.85$.

### Q37: Can the fraud engine run on real-time live calls?
- **Short Spoken Answer:** Yes, when audio loopback streaming is paired with Whisper utterance transcription, transcribing spoken segments every 2.5 seconds.

### Q38: Why use pre-compiled regexes rather than an LLM for scam classification?
- **Short Spoken Answer:** Pre-compiled regex executes in under 2 milliseconds with zero GPU memory and deterministic behavior, whereas an LLM adds 1-2 seconds of latency and is prone to hallucination.

---

## Category 6: Privacy, Capture & Retention (Q39 - Q46)

### Q39: What is Trustwire's retention policy, and what regulatory requirement does it satisfy?
- **Short Spoken Answer:** A strict 900-second (15-minute) rolling ceiling, satisfying the storage limitation principle of GDPR Article 5(1)(e).

### Q40: How is the 15-minute expiration physically enforced?
- **Short Spoken Answer:** An autonomous background daemon thread wakes up every 30 seconds and deletes all tracked files whose age exceeds 900 seconds.

### Q41: What happens if the computer crashes or loses power while files are in temporary storage?
- **Short Spoken Answer:** On reboot, `retention_manager.run_startup_recovery()` sweeps `temp_storage/` and deletes any stranded orphan files left behind.

### Q42: What Windows API is used to capture audio loopback without virtual audio cables?
- **Short Spoken Answer:** WASAPI (Windows Audio Session API) loopback mode via the Python `soundcard` library.

### Q43: What is the purpose of `_attach_thread_desktop()` in screen capture?
- **Short Spoken Answer:** It binds the capture worker thread to the active user interactive desktop handle via `ctypes.windll.user32.SetThreadDesktop`, preventing black frames across UAC boundaries.

### Q44: Does Trustwire write live screen capture frames permanently to disk?
- **Short Spoken Answer:** No. Live monitoring frames exist strictly in volatile RAM buffers (`np.ndarray`) and are garbage collected immediately after neural evaluation.

### Q45: Does `os.remove()` perform cryptographic disk shredding?
- **Short Spoken Answer:** No, it unlinks the file in the NTFS Master File Table. Modern SSDs utilize wear-leveling algorithms that render multi-pass magnetic overwrites ineffective.

### Q46: Can Trustwire decrypt DRM-protected video streams (e.g. Netflix)?
- **Short Spoken Answer:** No. Windows HDCP blocks screen grabbing on protected surfaces, returning blank black frames.

---

## Category 7: Performance, Benchmarking & Limitations (Q47 - Q54)

### Q47: What is the total RAM working set of Trustwire?
- **Short Spoken Answer:** Approximately 1.0 GB (~1,020 MB) encompassing backend, models, and Electron renderer.

### Q48: What is the measured inference latency of the Vision Transformer on CPU?
- **Short Spoken Answer:** ~205 milliseconds per 224x224 face crop using ONNX Runtime with AVX2 SIMD.

### Q49: What is the primary failure mode of video deepfake detectors?
- **Short Spoken Answer:** Heavy video compression (e.g. WhatsApp video with high CRF), which blurs out high-frequency spatial boundary artifacts.

### Q50: What is the primary failure mode of audio deepfake detectors?
- **Short Spoken Answer:** Band-limited telephone audio (8kHz GSM codecs) and loud musical background tracks that drown out vocal formants.

### Q51: How many automated tests exist in Trustwire, and what is their pass rate?
- **Short Spoken Answer:** 22 automated tests with a 100% pass rate.

### Q52: What is the difference between synchronous and asynchronous code in Trustwire?
- **Short Spoken Answer:** Asynchronous code handles non-blocking I/O (WebSockets/REST), while synchronous worker threads execute CPU-bound neural model inference.

### Q53: What license governs Trustwire?
- **Short Spoken Answer:** The open-source MIT License.

### Q54: What is your primary planned future enhancement for Trustwire v2?
- **Short Spoken Answer:** Cross-modal audio-visual attention for lip-sync discrepancy detection and NPU acceleration via OpenVINO / DirectML.

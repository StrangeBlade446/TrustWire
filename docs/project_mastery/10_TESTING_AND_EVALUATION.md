# Trustwire — Testing Suite, Forensic Benchmarking & Evaluation Protocol

> **Test Runner:** `pytest 8.4.2` with Python 3.11.9  
> **Automated Test Count:** 22 Automated Tests (100% Pass Rate)  
> **Forensic Benchmarks:** ASVspoof 2021, FaceForensics++ (FF++), Celeb-DF v2  

---

## 1. Automated Test Suite Architecture

Trustwire includes a comprehensive 22-test automated verification suite located in `tests/`. It covers REST APIs, neural detector wrappers, forensic logic, silence filtering, template matching, fraud regex rules, and privacy retention:

```
tests/
├── test_api.py              (6 tests: REST routes, capability auth, WebSocket lifecycle)
├── test_detectors.py        (8 tests: ViT inference, Haar cascades, skin tone, SynthID, Wav2Vec2)
├── test_fraud_engine.py     (4 tests: Regex rules, category compounding, educational dampening)
└── test_retention.py        (4 tests: Rolling buffer, 900s expiration, orphan sweeps, purge)
```

### Detailed Breakdown of Every Test Case:

```text
tests/test_api.py:
  1. test_health_check:
     - Verifies GET /api/health returns 200 OK.
     - Confirms version string, app name, and model readiness status flags.
  2. test_unauthorized_access:
     - Sends requests without X-Trustwire-Token header when TRUSTWIRE_DEV_NO_AUTH=0.
     - Confirms 401 Unauthorized status is strictly returned.
  3. test_models_info:
     - Verifies GET /api/models returns schema with ViT and Wav2Vec2 metadata.
  4. test_monitoring_lifecycle:
     - Tests POST /api/monitoring/start and POST /api/monitoring/stop.
     - Validates source enumeration on GET /api/monitoring/sources.
  5. test_alerts_lifecycle:
     - Dispatches synthetic alert, tests GET /api/alerts, acknowledges, dismisses, and clears.
  6. test_privacy_purge:
     - Creates dummy file, registers in retention, calls POST /api/privacy/purge, asserts file deleted.

tests/test_detectors.py:
  1. test_video_detector_available:
     - Verifies ONNX Runtime session loads the ViT model graph.
  2. test_video_detector_blank_frame:
     - Feeds solid black frame (1080p); confirms detector returns face_detected=False, score=0.0.
  3. test_video_detector_skin_tone_filter:
     - Tests YCrCb filter against pure blue box (rejected) vs synthetic flesh tone (passed).
  4. test_video_detector_synthid_watermark:
     - Overlays SynthID sparkle template on image; confirms normalized correlation score >= 0.55.
  5. test_audio_detector_available:
     - Verifies PyTorch Wav2Vec2 checkpoint is initialized and ready.
  6. test_audio_detector_silence_rejection:
     - Feeds zeros (RMS=0.0); confirms chunk is bypassed and returns score=0.0 without crash.
  7. test_audio_detector_synthetic_audio:
     - Feeds synthetic vocoder tone; confirms model scores > 0.60.
  8. test_audio_detector_temporal_aggregation:
     - Tests sliding window aggregator across multi-chunk synthetic and authentic mixtures.

tests/test_fraud_engine.py:
  1. test_fraud_engine_urgent_wire:
     - Tests "Urgent wire transfer required immediately"; asserts Critical scam severity.
  2. test_fraud_engine_otp_credential:
     - Tests "Please read me your OTP code"; asserts High severity credential alert.
  3. test_fraud_engine_educational_dampening:
     - Tests text with "cybersecurity awareness" prefix; asserts 60% score dampening.
  4. test_fraud_engine_clean_text:
     - Tests benign business conversation; asserts score=0.0 and zero alerts.

tests/test_retention.py:
  1. test_register_and_track_artifact:
     - Registers file; confirms entry in retention_manager registry with timestamp.
  2. test_automatic_expiration_cleanup:
     - Simulates artifact registered 901 seconds ago; confirms clean_expired() deletes file.
  3. test_startup_orphan_recovery:
     - Places unindexed file in temp_storage/; confirms run_startup_recovery() unlinks it.
  4. test_manual_purge_all:
     - Creates 5 files; calls purge_all(); confirms disk directory is completely empty.
```

### How to Run the Tests:
From the workspace root in PowerShell:
```powershell
python -m pytest tests/ -v
```

---

## 2. Forensic Evaluation Methodology & Research Benchmarks

In academic and industrial deepfake research, models are benchmarked against standardized public datasets:

| Modality | Standard Research Datasets | Primary Evaluation Focus |
| :--- | :--- | :--- |
| **Audio** | **ASVspoof 2019 / 2021 LA** (Logical Access) | Neural vocoders, WaveNet, Tacotron, VALL-E speech synthesis. |
| **Video** | **FaceForensics++ (FF++)** | Deepfakes, Face2Face, FaceSwap, NeuralTextures at raw, c23, c40 compression. |
| **Video** | **Celeb-DF v2** | High-visual-quality celebrity face-swaps with minimal boundary artifacts. |
| **Video** | **DFDC** (Deepfake Detection Challenge) | Real-world uncontrolled lighting, diverse ethnicities, heavy compression. |

---

## 3. Critical Methodological Principle: Preventing Data Leakage

A pervasive failure in naive deepfake detection research is **Identity Leakage**:
- If Actor "Alice" appears in the training set as both real and fake, and also appears in the test set, a deep neural network will simply memorize Alice's facial bone structure, skin texture, or vocal timbre.
- The model achieves $99\%$ accuracy on the test set, but fails catastrophically ($<55\%$) when deployed in the wild on an unseen person ("Bob").

### The Identity-Disjoint Protocol:
Trustwire's foundation models enforce strict **identity-disjoint evaluation**:
$$\text{Subjects}(\mathcal{D}_{\text{train}}) \cap \text{Subjects}(\mathcal{D}_{\text{test}}) = \emptyset$$
No individual's face or voice present in the training set may ever appear in testing or validation splits. The model is forced to learn *generalizable manipulation artifacts* (spectral phase inconsistencies, boundary blending seams, color disparity) rather than facial or acoustic identity.

---

## 4. The Domain Shift Problem & Cross-Dataset Generalization

**Domain Shift** occurs when the statistical distribution of the test environment diverges from the training distribution:
- **Compression Artifacts:** A model trained on lossless H.264 video ($\text{CRF} \approx 18$) often degrades when applied to heavily compressed social media video (TikTok or WhatsApp, $\text{CRF} \ge 32$), because JPEG/H.264 block-compression wipes out high-frequency GAN boundary textures.
- **Microphone Frequency Response:** Audio models trained on studio condenser microphones can mistake the band-limited response of cheap laptop microphones for vocoder filtering.

### Trustwire's Domain Shift Mitigations:
1. **Multi-Scale Face Sampling:** Haar cascading with dynamic bounding box padding ensures scale invariance.
2. **Skin-Tone Filtering:** Blocks non-face high-frequency textures from skewing the ViT.
3. **Multi-Chunk Audio Aggregation:** Evaluating median and ratio thresholds across 3-second windows prevents transient microphone noise spikes from triggering persistent alerts.
4. **Transparent Inconclusive States:** When face size is $<64$px or audio energy is below RMS $0.008$, Trustwire outputs `Inconclusive` rather than guessing with low confidence.

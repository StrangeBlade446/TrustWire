# Trustwire — Exhaustive Codebase File-by-File Walkthrough

> **Repository Root:** `c:\Users\Administrator\Desktop\VS Code\trustwire`  
> **Scope:** 100% of Backend, Desktop, Frontend, and Test Source Files  

---

## 1. Desktop Shell (`desktop/`)

### `desktop/main.js`
- **Purpose:** Electron main process orchestrating the desktop lifecycle, native window management, subprocess orchestration, and native OS notifications.
- **Key Functions:**
  - `getPythonExecutable()`: Probes system paths and `LOCALAPPDATA/Programs/Python/Python311` for a valid Python 3.11 binary.
  - `startPythonBackend()`: Spawns the FastAPI backend as a child process using `spawn()`. Pipes stdout and stderr to Electron logs.
  - `pollBackendHealth()`: Performs HTTP GET requests to `http://127.0.0.1:8765/api/health` every 400ms.
  - `createWindow()`: Builds the main 1280x820 Chromium BrowserWindow with `nodeIntegration: false`, `contextIsolation: true`. Injects `preload.js` bridge.
  - `createSplashWindow()`: Instantiates a frameless splash window rendering embedded `SPLASH_HTML` during backend boot.
  - IPC Handlers: Listens for `show-notification` events from the frontend renderer and invokes Windows native notifications (`new Notification({...})`).
- **Dependencies:** `electron`, `child_process`, `http`, `path`, `fs`.

### `package.json`
- **Purpose:** Root npm project configuration managing Electron packaging, scripts (`npm run dev`, `npm run build`), and dependencies.

---

## 2. Backend Application Core (`backend/`)

### `backend/config.py`
- **Purpose:** Centralized application configuration and runtime settings.
- **Key Class `Settings` (Pydantic BaseSettings):**
  - `app_name`: "Trustwire"
  - `app_version`: "1.0.0"
  - `host`: "127.0.0.1" (Strict localhost binding)
  - `port`: 8765
  - `api_token`: Reads from `TRUSTWIRE_API_TOKEN` environment variable or auto-generates a secure `uuid4().hex` string.
  - `temp_storage_dir`: Path to `temp_storage/` (ephemeral buffer).
  - `retention_seconds`: Default 900 (15 minutes).
  - `video_model_dir`: Path to `models/video/deepfake_v1`.
  - `audio_model_dir`: Path to `models/audio/wav2vec2_v2`.
- **Instance:** Global singleton `settings`.

### `backend/app.py`
- **Purpose:** FastAPI entry point providing REST endpoints, authentication dependencies, lifespan context management, and WebSocket real-time event broadcasting.
- **Key Functions & Endpoints:**
  - `lifespan(app)`: Context manager running `retention_manager.run_startup_recovery()` on startup and graceful teardown (`stop_monitoring()`, `purge_all()`) on shutdown.
  - `verify_token()`: Security dependency validating `X-Trustwire-Token` header against `settings.api_token`.
  - `GET /api/health`: Returns service health, version, token, and model readiness status.
  - `GET /api/models`: Returns forensic metadata, parameter sizes, and licenses for active neural models.
  - `GET /api/monitoring/sources`: Returns enumerated physical monitors and WASAPI loopback audio devices.
  - `GET /api/monitoring/status`: Returns active capture metrics (frames captured, processed, FPS, queue sizes).
  - `POST /api/monitoring/start`: Configures and starts screen/audio capture workers and inference thread.
  - `POST /api/monitoring/stop`: Terminates active workers and releases hardware handles.
  - `POST /api/analyze/upload`: Ingests video/audio file, saves to `temp_storage/`, registers in `RetentionManager`, invokes detectors, and returns comprehensive `MediaAnalysisResponse`.
  - `GET /api/alerts`: Retrieves alert history filtered by category, severity, or dismissed status.
  - `POST /api/alerts/{id}/acknowledge` & `dismiss`: Updates alert lifecycle state.
  - `DELETE /api/alerts`: Clears alert buffer.
  - `GET /api/privacy/status` & `POST /api/privacy/purge`: Inspects retention status and triggers manual disk wipe.
  - `WS /api/ws`: WebSocket endpoint broadcasting real-time alert objects and ping/pong heartbeats to UI clients.

---

## 3. Alerts & Privacy Subsystems

### `backend/alerts/hub.py`
- **Purpose:** Thread-safe in-memory alert dispatch hub with deduplication and WebSocket event fan-out.
- **Key Class `AlertItem` (Pydantic Model):**
  - Fields: `id`, `category` (`video_deepfake`, `audio_deepfake`, `scam_risk`), `severity` (`Low`, `Medium`, `High`, `Critical`), `title`, `explanation`, `evidence`, `timestamp`, `source`, `model_or_rule`, `confidence_score`, `suggested_action`, `acknowledged`, `dismissed`.
- **Key Class `AlertHub`:**
  - `dispatch_alert(...)`: Thread-safe alert creation with 3-second deduplication window to prevent UI spam from high-frequency video frames.
  - `broadcast_alert(alert)`: Schedules async broadcast across all connected WebSockets using `asyncio.run_coroutine_threadsafe()`.
  - Subscriber management: `add_subscriber()`, `remove_subscriber()`.

### `backend/privacy/retention.py`
- **Purpose:** Enforces the 15-minute (900s) rolling buffer privacy policy on disk.
- **Key Class `RetentionManager`:**
  - `register_artifact(file_path, tag)`: Stamps file path with current epoch timestamp in memory.
  - `clean_expired()`: Scans all registered artifacts. If $(t_{\text{now}} - t_{\text{artifact}}) > 900$, safely unlinks file and removes entry.
  - `_background_cleaner_loop()`: Daemon thread waking up every 30 seconds to call `clean_expired()`.
  - `run_startup_recovery()`: Recursively scans `temp_storage/` on boot and deletes any stranded files.
  - `purge_all()`: Instant complete manual deletion of all tracked files.

---

## 4. Hardware Capture Subsystem (`backend/capture/`)

### `backend/capture/screen.py`
- **Purpose:** Ultra-low latency Windows desktop screen grabbing.
- **Key Class `ScreenCaptureWorker`:**
  - Uses `mss.mss()` with Windows GDI BitBlt acceleration.
  - `_attach_thread_desktop()`: Uses `ctypes.windll.user32.SetThreadDesktop` to ensure desktop access stability.
  - Thread loop captures frames at `sample_interval_seconds` (1.0s) and enqueues into `frame_queue` (FIFO, `maxsize=3`).
  - Stale frame dropping: If queue is full, the oldest frame is discarded to guarantee zero latency lag.
  - `get_available_monitors()`: Static helper returning monitor geometry (`top`, `left`, `width`, `height`).

### `backend/capture/audio.py`
- **Purpose:** System audio loopback capture without requiring virtual audio cables.
- **Key Class `AudioLoopbackWorker`:**
  - Uses `soundcard.all_microphones(include_loopback=True)` to attach to the default Windows WASAPI output stream.
  - Records continuous blocks of float32 samples.
  - Aggregates samples into `chunk_duration_sec` (2.5s) buffers.
  - Calculates RMS energy ($E_{\text{RMS}}$).
  - Enqueues into `audio_queue` (`maxsize=5`).

### `backend/capture/manager.py`
- **Purpose:** Coordinates live capture workers with background forensic inference threads.
- **Key Class `LiveMonitoringCoordinator`:**
  - Owns instances of `ScreenCaptureWorker` and `AudioLoopbackWorker`.
  - `_inference_loop()`: Continuously consumes from `frame_queue` and `audio_queue`.
  - Passes frames to `video_detector.analyze_frame()`; triggers `alert_hub.dispatch_alert()` if $P \ge 0.52$.
  - Passes audio buffers to `audio_detector.analyze_samples()`; triggers alert if $P \ge 0.65$.
  - Maintains `recent_activity` statistics (processed frame counts, dropped frames, last scores).

---

## 5. Forensic Detection Engines (`backend/detectors/`)

### `backend/detectors/video/detector.py`
- **Purpose:** Vision Transformer deepfake face classifier with multi-scale SynthID watermark audit.
- **Key Classes:** `FrameEvidence`, `VideoAnalysisResult`, `VideoDeepfakeDetector`.
- **Key Methods:**
  - `_load_model()`: Initializes ONNX Runtime InferenceSession with CPU multi-threading.
  - `_detect_faces_and_crop(frame_bgr)`: Dual Haar cascades (`alt2`, `alt`) extracting face bounding boxes.
  - `_is_skin_tone_valid(face_bgr)`: YCrCb color space filter ($Cr \in [133, 173], Cb \in [77, 127]$).
  - `_detect_synthid_watermark(frame_bgr)`: Multi-scale normalized cross-correlation (scales 0.40 - 1.15) on Canny edge maps against `gemini_star_template.png`.
  - `_inspect_container_hardware(container)`: PyAV metadata scan for camera make/model vs software encoders.
  - `analyze_frame(frame_bgr, timestamp)`: Processes single live frame and returns `FrameEvidence`.
  - `analyze_video(video_path)`: Full temporal video analysis with frame sampling (1.0 fps) and aggregation.

### `backend/detectors/audio/detector.py`
- **Purpose:** Wav2Vec2 neural vocoder speech spoofing classifier.
- **Key Classes:** `ChunkEvidence`, `AudioAnalysisResult`, `AudioDeepfakeDetector`.
- **Key Methods:**
  - `_load_model()`: Loads `MelodyMachine/Deepfake-audio-detection-V2` via PyTorch in CPU float32 mode.
  - `_decode_and_resample(audio_path)`: PyAV audio stream extraction and resampling to 16,000 Hz mono PCM float32.
  - `analyze_samples(samples)`: Evaluates a 1D float32 numpy array, verifies RMS energy $\ge 0.008$, runs PyTorch forward pass, and returns $P(\text{Fake})$.
  - `analyze_audio(audio_path)`: Sliding window analysis (3.0s window, 1.5s stride), silence gating, and multi-chunk temporal aggregation.

---

## 6. Fraud Detection & Transcription (`backend/fraud/`, `backend/transcription/`)

### `backend/fraud/rules.py`
- **Purpose:** Regex taxonomy of 7 threat categories (`urgent_action`, `credential_theft`, `financial_coercion`, `authority_impersonation`, `unusual_payment`, `secrecy_pressure`, `lottery_prize`), pattern weights ($w_i \in [15, 45]$), negation windows, and educational whitelist patterns.

### `backend/fraud/engine.py`
- **Purpose:** Context-aware scam evaluation engine implementing the compounding category formula:
  $$S = \min\left(1.0, \frac{\sum w_i}{100} \cdot (1.0 + 0.3 \cdot (C - 1))\right)$$
  Includes negation windowing (ignores "do not share password") and educational context dampening.

### `backend/transcription/whisper_service.py`
- **Purpose:** Offline automatic speech recognition using `faster-whisper` (CTranslate2) `tiny` INT8 model with Silero VAD speech segmentation. Feeds transcribed text to `FraudEngine`.

---

## 7. Frontend Presentation Tier (`frontend/src/`)

### `frontend/src/App.tsx`
- **Purpose:** Top-level React router and application layout. Manages global WebSocket connection to `/api/ws`, handles incoming alerts, displays navigation sidebar, and renders `DisparityAlertPopup`.

### `frontend/src/services/api.ts`
- **Purpose:** Typed Axios HTTP client automatically attaching `X-Trustwire-Token` to all outbound requests. Exports helper functions: `getHealth()`, `getModels()`, `startMonitoring()`, `stopMonitoring()`, `uploadMedia()`, `getAlerts()`, `purgePrivacy()`.

### `frontend/src/views/`
- **`Dashboard.tsx`:** Executive overview showing detector statuses, quick monitoring toggle, system telemetry, and recent forensic alert log.
- **`LiveMonitoring.tsx`:** Real-time surveillance console with monitor selector, audio device picker, frame processing FPS gauge, live disparity meter, and event log.
- **`AnalyzeMedia.tsx`:** Static media file inspection workstation with drag-and-drop file uploader, temporal score timeline, face crop gallery, and downloadable forensic evidence report.
- **`AlertHistory.tsx`:** Filterable alert database with category, severity, and acknowledgment filters, export buttons, and remediation guidance.
- **`ModelsPerformance.tsx`:** Technical inspection panel detailing ViT and Wav2Vec2 architectures, checkpoint paths, measured inference latencies, parameter counts, and research paper citations.
- **`PrivacySettings.tsx`:** Privacy compliance console displaying active rolling buffer count, disk usage, countdown to expiration, and manual emergency wipe trigger.
- **`About.tsx`:** System documentation, open-source licenses (MIT, Apache-2.0), security disclosure, and project credits.

### `frontend/src/components/DisparityAlertPopup.tsx`
- **Purpose:** Sleek floating toast notification card rendering in the top-right corner whenever a critical synthetic media or fraud alert is broadcast via WebSocket. Features sound alert, severity badge, evidence breakdown, and one-click dismiss.

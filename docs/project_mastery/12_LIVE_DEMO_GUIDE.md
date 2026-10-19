# Trustwire — Evaluator Live Demonstration Guide & Script

> **Purpose:** Step-by-Step Practical Demonstration Playbook for Live Academic/Technical Evaluations  
> **Target Audience:** Demonstrator / Presenter defending Trustwire in real time  
> **Execution Duration:** 8 to 12 Minutes  

---

## 1. Pre-Demo Verification Checklist (Do 15 Minutes Prior)

Before presenting to evaluators, execute this strict 5-point sanity protocol:

- [ ] **Check 1: Python Runtime & Dependencies**
  Open PowerShell and verify Python 3.11:
  ```powershell
  python --version
  # Output must be Python 3.11.x
  ```
- [ ] **Check 2: Automated Test Suite Cleanliness**
  Execute the test suite to guarantee 100% operational readiness:
  ```powershell
  python -m pytest tests/ -q
  # Output must confirm: 22 passed in ~30s
  ```
- [ ] **Check 3: Port 8765 Availability**
  Confirm no stranded processes are occupying the API port:
  ```powershell
  Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue
  # If any output appears, run: Stop-Process -Name python -Force
  ```
- [ ] **Check 4: Checkpoint Files on Disk**
  Verify weights exist in `models/video/deepfake_v1/model.onnx` and `models/audio/wav2vec2_v2/`.
- [ ] **Check 5: Audio Endpoint Check**
  Verify default Windows speakers or headphones are active and audible.

---

## 2. Launching the Demonstration Workstation

Open PowerShell in the project directory:
```powershell
cd "c:\Users\Administrator\Desktop\VS Code\trustwire"
npm start
```
*Observe with the evaluators:*
1. The **Trustwire Splash Screen** appears immediately.
2. The splash screen displays `Initializing Forensic Core...` while spawning the backend subprocess.
3. Upon health check confirmation (`200 OK`), the splash transitions smoothly into the main dark-mode forensic workstation.

---

## 3. Demonstration Scenario 1: Static Multi-Modal Media Analysis

**Goal:** Prove forensic deepfake detection on an uploaded media file, highlighting dual-vector inspection, face cropping, skin validation, and privacy retention.

1. **Navigate:** Click **"Analyze Media"** in the left navigation sidebar.
2. **Explain the Modality:**
   > *"Here we have Trustwire's offline forensic workstation. When a suspicious video or audio file is received—such as an alleged executive announcement or a voice note—we can ingest it without sending a single byte to any cloud service."*
3. **Ingest Media:** Drag and drop a test media file (or click the file browser).
4. **Execution Walkthrough:**
   - Click **"Run Multi-Modal Analysis"**.
   - Point out the real-time processing indicator.
   - Explain the backend execution:
     > *"Under the hood, PyAV demuxes the video stream. Frames are extracted at 1 fps, passed through OpenCV's dual Haar cascade for face isolation, and filtered through our YCrCb skin chrominance matrix. The normalized 224x224 crops are evaluated by the Vision Transformer in ONNX Runtime. Simultaneously, the audio track is extracted, resampled to 16kHz, checked for silence, and processed by our Wav2Vec2 neural vocoder detector."*
5. **Review Results with Evaluators:**
   - **Overall Verdict Card:** Show whether the media is flagged as *"Likely authentic"* or *"Potentially manipulated"*.
   - **Confidence Score Gauge:** Show the calibrated probability meter.
   - **Forensic Evidence Summary:** Point out the identified timestamps and face bounding box coordinates.
   - **Watermark Audit:** Point out that Google SynthID edge template correlation returned negative (no generative watermark).
   - **Hardware Container Tags:** Show that the container lacked physical camera hardware metadata (e.g. `Lavf` software encoder detected).

---

## 4. Demonstration Scenario 2: Real-Time Live Desktop & Audio Monitoring

**Goal:** Demonstrate active background surveillance of on-screen video and system audio loopback with instant alert dispatch.

1. **Navigate:** Click **"Live Monitoring"** in the sidebar.
2. **Review Configuration Panel:**
   - Show the **Monitor Selector** (enumerating active displays via MSS).
   - Show the **Audio Device Selector** (enumerating WASAPI loopback speakers via Soundcard).
   - Point out that both **Video Analysis** and **Audio Analysis** toggles are active.
3. **Initiate Monitoring:**
   - Click the green **"Start Live Monitoring"** button.
   - Point out the active status indicator:
     - Real-time **Frame Rate** gauge (~1.0 fps).
     - **Frames Captured** and **Audio Chunks Processed** counters incrementing.
4. **Trigger Synthetic Disparity Alert:**
   - Play a short video or audio clip containing synthetic speech or facial manipulation on your display (or play a test video in VLC/browser).
   - Observe the live console:
     - The **Live Disparity Meter** spikes above threshold ($> 0.65$).
     - The **`DisparityAlertPopup` toast** animates in the top-right corner with a high-contrast red warning badge.
     - A native **Windows Notification Toast** appears in the Windows Action Center.
5. **Inspect the Alert Card:**
   - Click the alert card to expand details.
   - Show the detected category (`video_deepfake` or `audio_deepfake`).
   - Read the actionable remediation advice:
     > *"Suggested Action: Verify caller identity via a trusted secondary channel. Avoid taking actions based solely on video appearance."*
   - Click **"Acknowledge"** to mark the alert as addressed.
6. **Stop Monitoring:**
   - Click the red **"Stop Monitoring"** button.
   - Point out that capture threads terminate immediately and all hardware handles are released.

---

## 5. Demonstration Scenario 3: Provable Privacy & The 15-Minute Rolling Buffer

**Goal:** Convince technical evaluators that Trustwire cannot be weaponized as persistent spyware and strictly complies with data retention laws.

1. **Navigate:** Click **"Privacy Settings"** in the sidebar.
2. **Inspect the Active Storage Registry:**
   - Show the list of registered artifacts created during Scenarios 1 and 2.
   - Point out the **Time to Expiration Countdown** (e.g., `14m 22s remaining`).
   - Explain the mathematical policy:
     > *"Every temporary frame and uploaded video is registered in our `RetentionManager` with an epoch timestamp. An autonomous background daemon executes garbage collection every 30 seconds. If any artifact's age exceeds 900 seconds (15 minutes), it is permanently unlinked from disk."*
3. **Execute Emergency Wipe:**
   - Point out the red **"Emergency Secure Purge"** button.
   - Click the button.
   - Observe: The registry count drops to `0 Active Files`, disk usage drops to `0.0 MB`, and a confirmation banner verifies complete deletion.
   - Verify on disk: Open `temp_storage/` in Windows Explorer to show evaluators that the folder is completely empty.

---

## 6. Live Contingency Plan (What If Something Goes Wrong?)

| Potential Live Demo Glitch | Immediate Remediation Step |
| :--- | :--- |
| **Electron Window Hangs on White Screen** | Press `Ctrl + R` to reload the Chromium webview. The backend runs independently and state will reconnect immediately via WebSocket. |
| **Backend Port 8765 Conflict on Boot** | Open PowerShell, execute `Stop-Process -Name python -Force`, and restart via `npm start`. |
| **Audio Loopback Fails to Capture** | Confirm sound is actually playing through speakers. If using Bluetooth headphones, switch Windows audio output to default Realtek Speakers. |
| **Evaluator Questions "Is this really local?"** | Open Windows Task Manager -> Performance -> Wi-Fi/Ethernet. Show that network throughput is **0.0 Kbps** while running full forensic inference. |

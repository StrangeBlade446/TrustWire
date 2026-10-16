# Trustwire Privacy & Retention Policy Specification

Privacy is the foundational design pillar of Trustwire. The application is engineered to prevent surveillance, avoid accidental cloud data leakage, and ensure user control over all media capture.

## 1. Zero Cloud Transmission

- All model inference—visual manipulation scoring, synthetic voice analysis, and conversational fraud checks—runs 100% locally on your machine.
- No audio recordings, video frames, transcripts, or user telemetry are sent to remote servers.
- The backend binds exclusively to `127.0.0.1` (localhost).

## 2. Hardcoded 15-Minute Maximum Retention

- **Mandatory Expiration:** Any temporary media saved to disk during file inspection or diagnostic logging is assigned a maximum lifespan of 15 minutes (900 seconds).
- **Background Cleaner:** A daemon thread runs every 30 seconds to inspect the temporary storage directory and remove expired files.
- **Startup Crash Recovery:** If the computer loses power or the application process is terminated abruptly, the application automatically scrubs leftover temporary files on the next launch.
- **On-Demand Purging:** Users can immediately erase all temporary media at any time by clicking "Purge All Temp Media Now" in the Privacy settings.

## 3. Ephemeral In-Memory Live Monitoring

- During Live System Monitoring, screen frames and WASAPI loopback audio buffers are held in bounded memory queues.
- Frames are analyzed in real time and immediately discarded.
- No continuous audio or video files are written to disk during live monitoring.
- The user's webcam and physical microphone are never accessed by Trustwire.

## 4. Zero Raw Media in Alert History

- The alert database stores only forensic metadata (timestamp, alert category, severity, confidence score, triggering keywords, and suggested action).
- Raw video frames, full audio recordings, and private conversations are never stored in the alert history.

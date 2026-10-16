"""Trustwire Deepfake Video Detector
Extracts frames, performs face localization using OpenCV, runs ViT Deepfake Classifier via ONNX Runtime,
aggregates frame-level evidence, and produces structured forensic assessments.
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
import onnxruntime as ort
from pydantic import BaseModel, Field

from backend.config import settings

logger = logging.getLogger("trustwire.detectors.video")

class FrameEvidence(BaseModel):
    timestamp_seconds: float
    fake_score: float
    face_detected: bool
    bounding_box: Optional[List[int]] = None  # [x, y, w, h]

class VideoAnalysisResult(BaseModel):
    status: str  # "Ready", "Completed", "Inconclusive", "Unavailable", "Error"
    classification: str  # "Likely authentic", "Potentially manipulated", "Inconclusive", "Unavailable"
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    frames_analyzed: int
    suspicious_frames_count: int
    suspicious_timestamps: List[float]
    frame_evidences: List[FrameEvidence]
    evidence_summary: str
    model_name: str = "ViT Deepfake Image/Video Classifier (Quantized ONNX)"
    model_version: str = "1.0.0"
    processing_duration_ms: float
    limitations: str = "Probabilistic frame evaluation. Compressed or extreme lighting video may yield inconclusive scores."

class VideoDeepfakeDetector:
    """Forensic deepfake video detection using face cropping and ViT ONNX inference."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = Path(model_path or settings.video_model_onnx)
        self.session: Optional[ort.InferenceSession] = None
        self.face_cascade: Optional[cv2.CascadeClassifier] = None
        self.input_name: Optional[str] = None
        self._load_error: Optional[str] = None
        self._initialize_model()

    def _initialize_model(self):
        """Load the ONNX model and OpenCV face cascade."""
        try:
            if not self.model_path.exists():
                self._load_error = f"Model checkpoint not found at {self.model_path}"
                logger.warning(self._load_error)
                return

            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.inter_op_num_threads = 1
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options=opts,
                providers=['CPUExecutionProvider']
            )
            self.input_name = self.session.get_inputs()[0].name

            # Initialize OpenCV Face Detectors (alt2 is highly accurate, profileface detects angled faces)
            cascade_alt2 = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
            cascade_profile = cv2.data.haarcascades + 'haarcascade_profileface.xml'
            cascade_default = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            
            self.face_cascades = []
            for p in [cascade_alt2, cascade_profile, cascade_default]:
                if os.path.exists(p):
                    self.face_cascades.append(cv2.CascadeClassifier(p))
            
            logger.info(f"Video deepfake detector initialized with {len(self.face_cascades)} face cascades.")
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to initialize video detector: {e}")

    @property
    def is_available(self) -> bool:
        return self.session is not None

    def preprocess_image(self, bgr_img: np.ndarray) -> np.ndarray:
        """Convert BGR to RGB, resize to 224x224, and normalize with mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]."""
        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (224, 224), interpolation=cv2.INTER_LINEAR)
        # Normalize to [-1.0, 1.0]: (x / 255.0 - 0.5) / 0.5 = 2 * (x / 255.0) - 1.0
        norm = (resized.astype(np.float32) / 255.0 - 0.5) / 0.5
        # Layout: HWC to CHW
        transposed = np.transpose(norm, (2, 0, 1))
        # Add batch dim: NCHW
        return np.expand_dims(transposed, axis=0).astype(np.float32)

    def extract_face(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], bool, Optional[List[int]]]:
        """Detect and crop the primary face in the frame using multi-cascade detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for cascade in getattr(self, 'face_cascades', []):
            faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
            if len(faces) > 0:
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                margin_x = int(w * 0.15)
                margin_y = int(h * 0.15)
                x1 = max(0, x - margin_x)
                y1 = max(0, y - margin_y)
                x2 = min(frame.shape[1], x + w + margin_x)
                y2 = min(frame.shape[0], y + h + margin_y)
                cropped = frame[y1:y2, x1:x2]
                return cropped, True, [int(x), int(y), int(w), int(h)]

        # If no face is detected, return None rather than center-cropping background
        return None, False, None

    def analyze_frame(self, frame: np.ndarray, timestamp_seconds: float = 0.0) -> FrameEvidence:
        """Analyze a single video frame. Only runs ViT if a human face is verified."""
        if not self.is_available:
            return FrameEvidence(timestamp_seconds=timestamp_seconds, fake_score=0.0, face_detected=False)

        face_img, has_face, bbox = self.extract_face(frame)
        if not has_face or face_img is None or face_img.size == 0:
            # Non-face frame: do not score out-of-distribution background with face classifier
            return FrameEvidence(
                timestamp_seconds=round(timestamp_seconds, 2),
                fake_score=0.0,
                face_detected=False,
                bounding_box=None
            )

        tensor = self.preprocess_image(face_img)
        outputs = self.session.run(None, {self.input_name: tensor})
        logits = outputs[0]  # shape: (1, 2)
        # Softmax: id2label = {0: 'Real', 1: 'Fake'}
        exp = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        probs = exp / np.sum(exp, axis=-1, keepdims=True)
        fake_prob = float(probs[0][1])

        return FrameEvidence(
            timestamp_seconds=round(timestamp_seconds, 2),
            fake_score=round(fake_prob, 4),
            face_detected=True,
            bounding_box=bbox
        )

    def analyze_video(self, video_path: Path, sample_interval_seconds: float = 0.5, max_frames: int = 60) -> VideoAnalysisResult:
        """Decode video, sample frames, localize faces, evaluate with ViT, and aggregate results."""
        t0 = time.time()
        if not self.is_available:
            return VideoAnalysisResult(
                status="Unavailable",
                classification="Unavailable",
                confidence_score=0.0,
                frames_analyzed=0,
                suspicious_frames_count=0,
                suspicious_timestamps=[],
                frame_evidences=[],
                evidence_summary=f"Video detector unavailable: {self._load_error or 'Weights missing'}",
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        if not video_path.exists():
            return VideoAnalysisResult(
                status="Error",
                classification="Unavailable",
                confidence_score=0.0,
                frames_analyzed=0,
                suspicious_frames_count=0,
                suspicious_timestamps=[],
                frame_evidences=[],
                evidence_summary=f"Video file not found: {video_path}",
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return VideoAnalysisResult(
                status="Error",
                classification="Unavailable",
                confidence_score=0.0,
                frames_analyzed=0,
                suspicious_frames_count=0,
                suspicious_timestamps=[],
                frame_evidences=[],
                evidence_summary="Failed to open video file. File may be corrupted or codec unsupported.",
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = max(1, int(fps * sample_interval_seconds))
        frame_evidences: List[FrameEvidence] = []
        frame_idx = 0

        try:
            while cap.isOpened() and len(frame_evidences) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % frame_interval == 0:
                    ts = frame_idx / fps
                    evidence = self.analyze_frame(frame, timestamp_seconds=ts)
                    frame_evidences.append(evidence)
                frame_idx += 1
        finally:
            cap.release()

        duration_ms = round((time.time() - t0) * 1000, 2)
        total_frames = len(frame_evidences)

        if total_frames == 0:
            return VideoAnalysisResult(
                status="Completed",
                classification="Inconclusive",
                confidence_score=0.0,
                frames_analyzed=0,
                suspicious_frames_count=0,
                suspicious_timestamps=[],
                frame_evidences=[],
                evidence_summary="No readable frames could be extracted from video.",
                processing_duration_ms=duration_ms
            )

        # Forensic Face-Only Aggregation
        face_evidences = [ev for ev in frame_evidences if ev.face_detected]
        total_face_frames = len(face_evidences)

        if total_face_frames == 0:
            return VideoAnalysisResult(
                status="Completed",
                classification="Inconclusive",
                confidence_score=0.0,
                frames_analyzed=total_frames,
                suspicious_frames_count=0,
                suspicious_timestamps=[],
                frame_evidences=frame_evidences,
                evidence_summary=f"Inconclusive: No clear human faces detected across {total_frames} sampled frames. Facial deepfake analysis requires visible facial features.",
                processing_duration_ms=duration_ms
            )

        fake_scores = [ev.fake_score for ev in face_evidences]
        suspicious_evidences = [ev for ev in face_evidences if ev.fake_score >= 0.65]
        suspicious_count = len(suspicious_evidences)
        suspicious_timestamps = [ev.timestamp_seconds for ev in suspicious_evidences]
        suspicious_ratio = suspicious_count / float(total_face_frames)

        sorted_scores = sorted(fake_scores, reverse=True)
        top_k = max(1, int(np.ceil(total_face_frames * 0.25)))
        top_k_score = float(np.mean(sorted_scores[:top_k]))
        mean_face_score = float(np.mean(fake_scores))
        median_face_score = float(np.median(fake_scores))

        # A video is classified as manipulated only if a consistent portion of detected face frames show manipulation
        # (at least 35% of face frames suspicious AND top-k score >= 0.65), preventing 1-2 momentary blurs from alerting.
        if (suspicious_ratio >= 0.35 and top_k_score >= 0.65) or (total_face_frames <= 3 and mean_face_score >= 0.70):
            classification = "Potentially manipulated"
            confidence = round(top_k_score, 4)
            summary = (
                f"Potentially manipulated: {suspicious_count} of {total_face_frames} face-detected frames "
                f"({suspicious_ratio:.1%}) showed anomalous facial generation artifacts (mean top-tier fake score: {confidence:.2f})."
            )
        elif suspicious_ratio <= 0.15 and median_face_score < 0.40 and mean_face_score < 0.45:
            classification = "Likely authentic"
            confidence = round(1.0 - mean_face_score, 4)
            summary = (
                f"Likely authentic: No persistent facial manipulation artifacts detected across "
                f"{total_face_frames} face frames (mean fake score: {mean_face_score:.2f}, peak: {sorted_scores[0]:.2f})."
            )
        else:
            classification = "Inconclusive"
            confidence = round(mean_face_score, 4)
            summary = (
                f"Inconclusive: Sampled face frames showed borderline or inconsistent artifacts "
                f"({suspicious_count}/{total_face_frames} suspicious frames, mean score: {mean_face_score:.2f}). "
                f"Natural lighting variations or camera compression could not be ruled out."
            )

        return VideoAnalysisResult(
            status="Completed",
            classification=classification,
            confidence_score=confidence,
            frames_analyzed=total_frames,
            suspicious_frames_count=suspicious_count,
            suspicious_timestamps=suspicious_timestamps,
            frame_evidences=frame_evidences,
            evidence_summary=summary,
            processing_duration_ms=duration_ms
        )

# Global singleton
video_detector = VideoDeepfakeDetector()

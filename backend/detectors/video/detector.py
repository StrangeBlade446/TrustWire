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

            # Initialize OpenCV Face Detector (Haar cascade fallback is fast and robust on Windows)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            logger.info("Video deepfake detector initialized successfully.")
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

    def extract_face(self, frame: np.ndarray) -> Tuple[np.ndarray, bool, Optional[List[int]]]:
        """Detect and crop the primary face in the frame, or return centered crop if none detected."""
        if self.face_cascade is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
            if len(faces) > 0:
                # Select the largest face by area
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                # Add 15% margin around the face
                margin_x = int(w * 0.15)
                margin_y = int(h * 0.15)
                x1 = max(0, x - margin_x)
                y1 = max(0, y - margin_y)
                x2 = min(frame.shape[1], x + w + margin_x)
                y2 = min(frame.shape[0], y + h + margin_y)
                cropped = frame[y1:y2, x1:x2]
                return cropped, True, [int(x), int(y), int(w), int(h)]

        # Center crop fallback
        h, w = frame.shape[:2]
        min_dim = min(h, w)
        start_y = (h - min_dim) // 2
        start_x = (w - min_dim) // 2
        return frame[start_y:start_y+min_dim, start_x:start_x+min_dim], False, None

    def analyze_frame(self, frame: np.ndarray, timestamp_seconds: float = 0.0) -> FrameEvidence:
        """Analyze a single video frame."""
        if not self.is_available:
            return FrameEvidence(timestamp_seconds=timestamp_seconds, fake_score=0.0, face_detected=False)

        face_img, has_face, bbox = self.extract_face(frame)
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
            face_detected=has_face,
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

        # Forensic Aggregation
        fake_scores = [ev.fake_score for ev in frame_evidences]
        suspicious_evidences = [ev for ev in frame_evidences if ev.fake_score >= 0.65]
        suspicious_count = len(suspicious_evidences)
        suspicious_timestamps = [ev.timestamp_seconds for ev in suspicious_evidences]

        # Top 10% high-confidence percentile aggregation
        sorted_scores = sorted(fake_scores, reverse=True)
        top_k = max(1, int(np.ceil(total_frames * 0.15)))
        aggregate_score = float(np.mean(sorted_scores[:top_k]))

        # Classification decision boundaries
        if aggregate_score >= 0.65:
            classification = "Potentially manipulated"
            summary = (
                f"Potentially manipulated: {suspicious_count} of {total_frames} sampled frames showed "
                f"anomalous facial generation artifacts (mean top-tier fake score: {aggregate_score:.2f})."
            )
        elif aggregate_score < 0.35:
            classification = "Likely authentic"
            summary = (
                f"Likely authentic: No significant facial manipulation artifacts detected across "
                f"{total_frames} sampled frames (peak score: {sorted_scores[0]:.2f})."
            )
        else:
            classification = "Inconclusive"
            summary = (
                f"Inconclusive: Sampled frames showed boundary scores (aggregate: {aggregate_score:.2f}). "
                f"Visual artifacts could not be definitively separated from natural compression."
            )

        return VideoAnalysisResult(
            status="Completed",
            classification=classification,
            confidence_score=round(aggregate_score, 4),
            frames_analyzed=total_frames,
            suspicious_frames_count=suspicious_count,
            suspicious_timestamps=suspicious_timestamps,
            frame_evidences=frame_evidences,
            evidence_summary=summary,
            processing_duration_ms=duration_ms
        )

# Global singleton
video_detector = VideoDeepfakeDetector()

"""Trustwire Deepfake Audio & Voice Cloning Detector
Extracts and resamples audio to 16kHz mono, applies Wav2Vec2 audio feature extraction,
performs chunked inference, identifies suspicious time ranges, and produces structured forensic assessments.
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import torch
import av
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
from pydantic import BaseModel, Field

from backend.config import settings

logger = logging.getLogger("trustwire.detectors.audio")

class AudioChunkEvidence(BaseModel):
    start_seconds: float
    end_seconds: float
    fake_score: float
    is_suspicious: bool

class AudioAnalysisResult(BaseModel):
    status: str  # "Ready", "Completed", "Inconclusive", "Unavailable", "Error"
    classification: str  # "Likely authentic", "Potentially synthetic", "Inconclusive", "Unavailable"
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    audio_duration_seconds: float
    chunks_analyzed: int
    suspicious_time_ranges: List[List[float]]  # [[start_sec, end_sec], ...]
    chunk_evidences: List[AudioChunkEvidence]
    evidence_summary: str
    model_name: str = "Wav2Vec2 Sequence Audio Spoofing Classifier"
    model_version: str = "2.0.0"
    processing_duration_ms: float
    limitations: str = "Differentiates synthetic speech vs natural human acoustic properties. Does not claim speaker identity verification."

class AudioDeepfakeDetector:
    """Forensic audio spoofing and voice cloning detection using Wav2Vec2."""

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = Path(model_dir or settings.audio_model_dir)
        self.session = None
        self.model = None
        self.feature_extractor = None
        self.model_name = "Wav2Vec2 Sequence Audio Spoofing Classifier"
        self._load_error: Optional[str] = None
        self._initialize_model()

    def _initialize_model(self):
        """Load Wav2Vec2 model (INT8 ONNX preferred, PyTorch fallback)."""
        onnx_path = self.model_dir / "wav2vec2_large_xlsr_int8.onnx"
        if onnx_path.exists():
            try:
                import onnxruntime as ort
                sess_options = ort.SessionOptions()
                sess_options.intra_op_num_threads = 2
                sess_options.inter_op_num_threads = 1
                sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                self.session = ort.InferenceSession(str(onnx_path), sess_options=sess_options, providers=["CPUExecutionProvider"])
                self.model_name = "Wav2Vec2 Large XLSR Audio Spoofing Classifier (INT8 ONNX)"
                logger.info("Audio deepfake detector initialized successfully using Wav2Vec2 INT8 ONNX.")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize ONNX audio session: {e}, falling back to PyTorch.")

        try:
            safetensors_path = self.model_dir / "model.safetensors"
            if not safetensors_path.exists():
                self._load_error = f"Model checkpoint not found at {safetensors_path}"
                logger.warning(self._load_error)
                return

            self.feature_extractor = AutoFeatureExtractor.from_pretrained(str(self.model_dir))
            self.model = AutoModelForAudioClassification.from_pretrained(str(self.model_dir))
            self.model.eval()
            self.model_name = "Wav2Vec2 Sequence Audio Spoofing Classifier"
            logger.info("Audio deepfake detector initialized successfully using PyTorch.")
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to initialize audio detector: {e}")

    @property
    def is_available(self) -> bool:
        return self.session is not None or (self.model is not None and self.feature_extractor is not None)

    def decode_audio(self, audio_path: Path, target_sr: int = 16000) -> Tuple[np.ndarray, float]:
        """Decode audio to 16kHz mono float32 numpy array using PyAV."""
        container = av.open(str(audio_path))
        audio_stream = next((s for s in container.streams if s.type == 'audio'), None)
        if audio_stream is None:
            container.close()
            raise ValueError("No audio stream found in media file.")

        resampler = av.AudioResampler(format='fltp', layout='mono', rate=target_sr)
        samples_list = []

        for frame in container.decode(audio_stream):
            resampled = resampler.resample(frame)
            if resampled:
                for r_frame in resampled:
                    # Convert to numpy 1D array
                    arr = r_frame.to_ndarray()
                    samples_list.append(arr[0])

        container.close()
        if not samples_list:
            raise ValueError("No audio samples could be decoded.")

        full_audio = np.concatenate(samples_list, axis=0)
        duration_sec = len(full_audio) / float(target_sr)
        return full_audio, duration_sec

    def analyze_samples(self, samples_16k: np.ndarray, start_sec: float = 0.0) -> float:
        """Run inference on a single 16kHz mono chunk."""
        if not self.is_available:
            return 0.0

        # Silence / ambient threshold (RMS energy < 0.008)
        # Prevents background ambient hiss/silence from triggering false synthetic scores.
        rms = float(np.sqrt(np.mean(samples_16k ** 2))) if len(samples_16k) > 0 else 0.0
        if rms < 0.008:
            return 0.0

        if self.session is not None:
            # Wav2Vec2 Large XLSR ONNX evaluation with zero-mean unit-variance normalization
            waveform = (samples_16k - float(np.mean(samples_16k))) / float(
                np.sqrt(np.var(samples_16k) + 1e-7)
            )
            input_values = waveform.reshape(1, -1).astype(np.float32)
            attention_mask = np.ones(input_values.shape, dtype=np.int32)
            try:
                out = self.session.run(None, {"input_values": input_values, "attention_mask": attention_mask})
                logits = out[0][0]
                shifted = logits - np.max(logits)
                probs = np.exp(shifted) / np.sum(np.exp(shifted))
                return float(probs[1])  # Class 0: Real, Class 1: Fake
            except Exception as e:
                logger.error(f"ONNX audio inference failure: {e}")
                return 0.0

        tensor_samples = torch.from_numpy(samples_16k).float()
        inputs = self.feature_extractor(tensor_samples, sampling_rate=16000, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
            # Identify fake index dynamically from label2id or default to 0 (fake in checkpoint)
            fake_idx = 0
            if hasattr(self.model, "config") and hasattr(self.model.config, "label2id"):
                for name, idx in self.model.config.label2id.items():
                    if any(k in name.lower() for k in ["fake", "synthetic", "spoof"]):
                        fake_idx = int(idx)
                        break
            fake_prob = float(probs[fake_idx])

        return fake_prob

    def analyze_audio(self, audio_path: Path, chunk_duration_sec: float = 3.0, stride_sec: float = 1.5) -> AudioAnalysisResult:
        """Analyze full audio recording in sliding chunks and aggregate evidence."""
        t0 = time.time()
        if not self.is_available:
            return AudioAnalysisResult(
                status="Unavailable",
                classification="Unavailable",
                confidence_score=0.0,
                audio_duration_seconds=0.0,
                chunks_analyzed=0,
                suspicious_time_ranges=[],
                chunk_evidences=[],
                evidence_summary=f"Audio detector unavailable: {self._load_error or 'Weights missing'}",
                model_name=self.model_name,
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        if not audio_path.exists():
            return AudioAnalysisResult(
                status="Error",
                classification="Unavailable",
                confidence_score=0.0,
                audio_duration_seconds=0.0,
                chunks_analyzed=0,
                suspicious_time_ranges=[],
                chunk_evidences=[],
                evidence_summary=f"Audio file not found: {audio_path}",
                model_name=self.model_name,
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        try:
            samples, total_duration = self.decode_audio(audio_path, target_sr=16000)
        except Exception as e:
            return AudioAnalysisResult(
                status="Error",
                classification="Unavailable",
                confidence_score=0.0,
                audio_duration_seconds=0.0,
                chunks_analyzed=0,
                suspicious_time_ranges=[],
                chunk_evidences=[],
                evidence_summary=f"Audio decoding failure: {str(e)}",
                model_name=self.model_name,
                processing_duration_ms=round((time.time() - t0) * 1000, 2)
            )

        chunk_size = int(chunk_duration_sec * 16000)
        stride_size = int(stride_sec * 16000)

        chunk_evidences: List[AudioChunkEvidence] = []
        chunk_rms_list: List[float] = []
        suspicious_ranges: List[List[float]] = []

        # If audio is shorter than a single chunk, evaluate the full recording once
        if len(samples) < chunk_size:
            rms_val = float(np.sqrt(np.mean(samples ** 2))) if len(samples) > 0 else 0.0
            chunk_rms_list.append(rms_val)
            score = self.analyze_samples(samples)
            is_susp = score >= 0.70
            chunk_evidences.append(AudioChunkEvidence(
                start_seconds=0.0,
                end_seconds=round(total_duration, 2),
                fake_score=round(score, 4),
                is_suspicious=is_susp
            ))
            if is_susp:
                suspicious_ranges.append([0.0, round(total_duration, 2)])
        else:
            for start_idx in range(0, len(samples) - chunk_size // 2, stride_size):
                end_idx = min(len(samples), start_idx + chunk_size)
                chunk_data = samples[start_idx:end_idx]
                if len(chunk_data) < 16000:  # Minimum 1 second for feature extractor
                    break

                start_time = round(start_idx / 16000.0, 2)
                end_time = round(end_idx / 16000.0, 2)

                rms_val = float(np.sqrt(np.mean(chunk_data ** 2))) if len(chunk_data) > 0 else 0.0
                chunk_rms_list.append(rms_val)

                score = self.analyze_samples(chunk_data)
                is_susp = score >= 0.70

                chunk_evidences.append(AudioChunkEvidence(
                    start_seconds=start_time,
                    end_seconds=end_time,
                    fake_score=round(score, 4),
                    is_suspicious=is_susp
                ))

                if is_susp:
                    # Merge consecutive ranges if continuous
                    if suspicious_ranges and abs(suspicious_ranges[-1][1] - start_time) <= stride_sec:
                        suspicious_ranges[-1][1] = end_time
                    else:
                        suspicious_ranges.append([start_time, end_time])

        duration_ms = round((time.time() - t0) * 1000, 2)
        total_chunks = len(chunk_evidences)

        if total_chunks == 0:
            return AudioAnalysisResult(
                status="Completed",
                classification="Inconclusive",
                confidence_score=0.0,
                audio_duration_seconds=total_duration,
                chunks_analyzed=0,
                suspicious_time_ranges=[],
                chunk_evidences=[],
                evidence_summary="Recording was too short to perform acoustic spoofing analysis.",
                model_name=self.model_name,
                processing_duration_ms=duration_ms
            )

        # Separate active speech chunks from ambient/silent chunks
        speech_indices = [i for i, r in enumerate(chunk_rms_list) if r >= 0.008]
        speech_scores = [chunk_evidences[i].fake_score for i in speech_indices]

        # Case 1: No active speech detected (ambient microphone noise or silence)
        if len(speech_scores) == 0:
            return AudioAnalysisResult(
                status="Completed",
                classification="Likely authentic",
                confidence_score=0.0,
                audio_duration_seconds=round(total_duration, 2),
                chunks_analyzed=total_chunks,
                suspicious_time_ranges=[],
                chunk_evidences=chunk_evidences,
                evidence_summary="Likely authentic: No synthetic voice or neural vocoder patterns detected. Audio consists of natural ambient sound or background silence.",
                model_name=self.model_name,
                processing_duration_ms=duration_ms
            )

        # Case 2: Speech segments present - evaluate only active speech segments
        sorted_speech = sorted(speech_scores, reverse=True)
        top_k = max(1, int(np.ceil(len(speech_scores) * 0.25)))
        aggregate_score = float(np.mean(sorted_speech[:top_k]))
        mean_speech_score = float(np.mean(speech_scores))
        suspicious_chunk_count = len([s for s in speech_scores if s >= 0.70])
        suspicious_ratio = suspicious_chunk_count / float(len(speech_scores))

        # Require aggregate synthetic vocoder anomalies across active speech
        if (aggregate_score >= 0.70 and suspicious_chunk_count >= 2) or (len(speech_scores) == 1 and aggregate_score >= 0.70):
            classification = "Potentially synthetic"
            summary = (
                f"Potentially synthetic: {len(suspicious_ranges)} suspicious acoustic segments detected "
                f"({suspicious_chunk_count}/{len(speech_scores)} active speech segments, peak fake score: {sorted_speech[0]:.2f}, "
                f"aggregate score: {aggregate_score:.2f}). Acoustic features match synthetic speech generation models."
            )
        elif aggregate_score < 0.35 and suspicious_chunk_count == 0:
            classification = "Likely authentic"
            summary = (
                f"Likely authentic: No significant synthetic voice or neural vocoder patterns detected "
                f"across {len(speech_scores)} speech segments (mean score: {mean_speech_score:.2f}, peak: {sorted_speech[0]:.2f})."
            )
        else:
            classification = "Inconclusive"
            summary = (
                f"Inconclusive: Acoustic score fell in borderline range (aggregate: {aggregate_score:.2f}, "
                f"suspicious ratio: {suspicious_ratio:.1%}). Background noise, microphone clipping, or reverberation may have affected inference."
            )

        return AudioAnalysisResult(
            status="Completed",
            classification=classification,
            confidence_score=round(aggregate_score, 4),
            audio_duration_seconds=round(total_duration, 2),
            chunks_analyzed=total_chunks,
            suspicious_time_ranges=suspicious_ranges,
            chunk_evidences=chunk_evidences,
            evidence_summary=summary,
            model_name=self.model_name,
            processing_duration_ms=duration_ms
        )

# Global singleton
audio_detector = AudioDeepfakeDetector()

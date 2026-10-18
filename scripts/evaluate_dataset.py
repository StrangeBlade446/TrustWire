"""Trustwire Dataset Evaluation & Benchmark Script
Evaluates Trustwire's detectors against the labeled authenticity dataset at:
C:\\Users\\Administrator\\Desktop\\VS Code\\Reforged\\data\\authenticity
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.detectors.audio.detector import audio_detector
from backend.detectors.video.detector import video_detector

DATASET_ROOT = Path(r"C:\Users\Administrator\Desktop\VS Code\Reforged\data\authenticity")

REAL_CAMERA_DIR = Path(r"C:\Users\Administrator\Desktop\data\video\real")
HF_FAKE_DIR = DATASET_ROOT / "audio" / "huggingface-deepfake-audio-v4" / "fake"

def benchmark_audio(num_samples: int = 5):
    print("=" * 60)
    print("BENCHMARKING AUDIO DETECTOR ON REAL CAMERA & SYNTHETIC DATASETS")
    print("=" * 60)
    
    # 1. Real authentic smartphone videos
    real_files = list(REAL_CAMERA_DIR.glob("PXL_*.mp4"))[:num_samples]
    # 2. Modern synthetic speech (ElevenLabs / vocoder deepfakes)
    fake_files = list(HF_FAKE_DIR.glob("*.flac"))[:num_samples]
    
    print(f"Found {len(real_files)} real samples and {len(fake_files)} fake samples for evaluation.\n")
    
    real_results = []
    print("--- REAL (AUTHENTIC) SMARTPHONE AUDIO SAMPLES ---")
    for f in real_files:
        res = audio_detector.analyze_audio(f)
        correct = res.classification == "Likely authentic"
        real_results.append((f.name, res.classification, res.confidence_score, correct))
        print(f"File: {f.name} | Predicted: {res.classification} (Score: {res.confidence_score:.3f}) | {'PASS' if correct else 'FAIL'}")
        
    fake_results = []
    print("\n--- FAKE (SYNTHETIC) SPEECH SAMPLES ---")
    for f in fake_files:
        res = audio_detector.analyze_audio(f)
        correct = res.classification == "Potentially synthetic"
        fake_results.append((f.name, res.classification, res.confidence_score, correct))
        print(f"File: {f.name} | Predicted: {res.classification} (Score: {res.confidence_score:.3f}) | {'PASS' if correct else 'FAIL'}")
        
    total = len(real_results) + len(fake_results)
    passed = sum(1 for _, _, _, c in real_results if c) + sum(1 for _, _, _, c in fake_results if c)
    acc = (passed / total) * 100 if total > 0 else 0
    print(f"\nAudio Accuracy: {passed}/{total} ({acc:.1f}%)\n")
    return acc

def benchmark_video(num_samples: int = 3):
    print("=" * 60)
    print("BENCHMARKING VIDEO DETECTOR ON LABELED DATASET")
    print("=" * 60)
    
    video_base = DATASET_ROOT / "video"
    
    # In DFDC style, '01__*.mp4' are real, '01_02__*.mp4' are manipulated
    real_files = [f for f in video_base.glob("*.mp4") if not "__" in f.name or f.name.count("_") <= 2][:num_samples]
    fake_files = [f for f in video_base.glob("*.mp4") if f.name.count("_") > 2][:num_samples]
    
    print(f"Evaluating {len(real_files)} real videos and {len(fake_files)} fake videos (max 10 frames each)...\n")
    
    real_results = []
    print("--- REAL VIDEOS ---")
    for f in real_files:
        res = video_detector.analyze_video(f, sample_interval_seconds=1.0, max_frames=10)
        correct = res.classification == "Likely authentic"
        real_results.append((f.name, res.classification, res.confidence_score, correct))
        print(f"File: {f.name} | Predicted: {res.classification} (Score: {res.confidence_score:.3f}) | {'PASS' if correct else 'FAIL'}")
        
    fake_results = []
    print("\n--- FAKE VIDEOS ---")
    for f in fake_files:
        res = video_detector.analyze_video(f, sample_interval_seconds=1.0, max_frames=10)
        correct = res.classification == "Potentially manipulated"
        fake_results.append((f.name, res.classification, res.confidence_score, correct))
        print(f"File: {f.name} | Predicted: {res.classification} (Score: {res.confidence_score:.3f}) | {'PASS' if correct else 'FAIL'}")
        
    total = len(real_results) + len(fake_results)
    passed = sum(1 for _, _, _, c in real_results if c) + sum(1 for _, _, _, c in fake_results if c)
    acc = (passed / total) * 100 if total > 0 else 0
    print(f"\nVideo Accuracy: {passed}/{total} ({acc:.1f}%)\n")
    return acc

if __name__ == "__main__":
    benchmark_audio(5)
    benchmark_video(2)

"""Script to benchmark and calibrate AudioDeepfakeDetector
against generated audio models (MelGAN, Parallel WaveGAN, HiFi-GAN, WaveGlow, ESPnet)
and real recorded smartphone camera audio.
"""

import os
import sys
import time
from pathlib import Path
import numpy as np

# Set project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.detectors.audio.detector import audio_detector

def run_calibration_benchmark(samples_per_category: int = 5):
    print("=" * 70, flush=True)
    print("TRUSTWIRE AUDIO DETECTOR CALIBRATION BENCHMARK", flush=True)
    print(f"Model: {audio_detector.model_name}", flush=True)
    print(f"Available: {audio_detector.is_available}", flush=True)
    print("=" * 70, flush=True)

    gen_root = Path(r"C:\Users\Administrator\Downloads\generated_audio\generated_audio")
    real_root = Path(r"C:\Users\Administrator\Desktop\data\video\real")

    results = {}

    # 1. Test Generated Audio Subdirectories
    if gen_root.exists():
        subdirs = [d for d in gen_root.iterdir() if d.is_dir()]
        print(f"\nFound {len(subdirs)} generated vocoder categories.", flush=True)

        for sdir in sorted(subdirs, key=lambda x: x.name):
            cat_name = sdir.name
            wav_files = []
            for root, dirs, files in os.walk(sdir):
                for f in files:
                    if f.lower().endswith(".wav"):
                        wav_files.append(os.path.join(root, f))
                        if len(wav_files) >= samples_per_category:
                            break
                if len(wav_files) >= samples_per_category:
                    break

            cat_scores = []
            cat_verdicts = []
            cat_durations = []

            for w_path in wav_files:
                try:
                    res = audio_detector.analyze_audio(Path(w_path))
                    cat_scores.append(res.confidence_score)
                    cat_verdicts.append(res.classification)
                    cat_durations.append(res.audio_duration_seconds)
                except Exception as e:
                    print(f"  Error on {w_path}: {e}", flush=True)

            avg_score = float(np.mean(cat_scores)) if cat_scores else 0.0
            fake_count = sum(1 for v in cat_verdicts if v == "Potentially synthetic")
            results[cat_name] = {
                "type": "Fake (Generated)",
                "total_tested": len(cat_scores),
                "avg_score": avg_score,
                "scores": cat_scores,
                "verdicts": cat_verdicts,
                "fake_detected_count": fake_count,
                "detection_rate": (fake_count / len(cat_scores)) if cat_scores else 0.0
            }

            print(f"[{cat_name}] ({len(cat_scores)} samples)", flush=True)
            print(f"  Avg Score: {avg_score:.4f} | Detections: {fake_count}/{len(cat_scores)} ({results[cat_name]['detection_rate']*100:.1f}%)", flush=True)
            for idx, (sc, vd) in enumerate(zip(cat_scores, cat_verdicts)):
                print(f"    sample_{idx+1}: score={sc:.4f} => {vd}", flush=True)

    # 2. Test Real Audio from real smartphone videos
    if real_root.exists():
        real_files = [f for f in real_root.iterdir() if f.suffix.lower() in [".mp4", ".mov", ".wav", ".mp3"]]
        real_sample = real_files[:samples_per_category * 2]
        real_scores = []
        real_verdicts = []

        print(f"\n[Real Smartphone Recordings] ({len(real_sample)} samples)", flush=True)
        for r_path in real_sample:
            try:
                res = audio_detector.analyze_audio(r_path)
                real_scores.append(res.confidence_score)
                real_verdicts.append(res.classification)
            except Exception as e:
                print(f"  Error on {r_path.name}: {e}", flush=True)

        avg_real = float(np.mean(real_scores)) if real_scores else 0.0
        auth_count = sum(1 for v in real_verdicts if v == "Likely authentic")
        results["REAL_SMARTPHONE"] = {
            "type": "Real",
            "total_tested": len(real_scores),
            "avg_score": avg_real,
            "scores": real_scores,
            "verdicts": real_verdicts,
            "authentic_count": auth_count,
            "accuracy": (auth_count / len(real_scores)) if real_scores else 0.0
        }
        print(f"  Avg Score: {avg_real:.4f} | Authentic: {auth_count}/{len(real_scores)} ({results['REAL_SMARTPHONE']['accuracy']*100:.1f}%)", flush=True)
        for idx, (sc, vd) in enumerate(zip(real_scores, real_verdicts)):
            print(f"    sample_{idx+1} ({real_sample[idx].name}): score={sc:.4f} => {vd}", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("SUMMARY OF BENCHMARK FINDINGS:", flush=True)
    print("=" * 70, flush=True)
    for name, r in results.items():
        if r["type"] == "Real":
            print(f"REAL: {name:40s} | Avg Score: {r['avg_score']:.4f} | Accuracy: {r['accuracy']*100:.1f}%", flush=True)
        else:
            print(f"FAKE: {name:40s} | Avg Score: {r['avg_score']:.4f} | Recall: {r['detection_rate']*100:.1f}%", flush=True)

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_calibration_benchmark(samples_per_category=count)

import React from 'react';
import {
  Shield,
  Award
} from 'lucide-react';

export const About: React.FC = () => {
  return (
    <div className="p-8 space-y-8 max-w-4xl mx-auto">
      {/* Hero Header */}
      <div className="text-center space-y-3 pb-8 border-b border-border">
        <div className="inline-flex p-3 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400 mb-2">
          <Shield className="w-10 h-10" />
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Trustwire</h1>
        <p className="text-base text-teal-300 font-medium">Detect deception before it costs you.</p>
        <p className="text-xs text-gray-400 max-w-xl mx-auto leading-relaxed">
          Autonomous real-time Windows forensic system combining neural facial manipulation classification,
          synthetic voice acoustic discrimination, and context-aware financial fraud protection.
        </p>
        <div className="flex items-center justify-center gap-2 pt-2 text-xs font-mono text-gray-500">
          <span>Release v1.0.0</span>
          <span>•</span>
          <span>MIT License</span>
          <span>•</span>
          <span>Windows 10/11 x64</span>
        </div>
      </div>

      {/* Model & Library Attribution Grid */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <Award className="w-4 h-4 text-teal-400" />
          Model Provenance & License Attributions
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl border border-border bg-panel space-y-2">
            <div className="font-semibold text-white">Vision Transformer Deepfake Classifier (ViT)</div>
            <div className="text-gray-400 font-mono text-[11px]">onnx-community/deepfake_vs_real_image_detection-ONNX</div>
            <p className="text-gray-400 text-[11px]">
              Trained on FaceForensics++ and deepfake benchmarks. Exported to quantized ONNX for sub-250ms local CPU execution.
            </p>
            <div className="text-teal-400 font-mono text-[10px]">License: Apache-2.0</div>
          </div>

          <div className="p-4 rounded-xl border border-border bg-panel space-y-2">
            <div className="font-semibold text-white">Wav2Vec2 Sequence Audio Spoofing Classifier</div>
            <div className="text-gray-400 font-mono text-[11px]">MelodyMachine/Deepfake-audio-detection-V2</div>
            <p className="text-gray-400 text-[11px]">
              Trained on ASVspoof benchmarks for acoustic artifact discrimination between biological speech and neural vocoders.
            </p>
            <div className="text-teal-400 font-mono text-[10px]">License: MIT</div>
          </div>

          <div className="p-4 rounded-xl border border-border bg-panel space-y-2">
            <div className="font-semibold text-white">Faster-Whisper Speech Recognition (CTranslate2)</div>
            <div className="text-gray-400 font-mono text-[11px]">OpenAI / Systran / faster-whisper</div>
            <p className="text-gray-400 text-[11px]">
              High-efficiency CTranslate2 speech-to-text inference engine running offline int8 quantized Whisper models.
            </p>
            <div className="text-teal-400 font-mono text-[10px]">License: MIT</div>
          </div>

          <div className="p-4 rounded-xl border border-border bg-panel space-y-2">
            <div className="font-semibold text-white">Windows WASAPI Audio & Screen Capture Core</div>
            <div className="text-gray-400 font-mono text-[11px]">soundcard (WASAPI Loopback) & mss (DirectX/GDI)</div>
            <p className="text-gray-400 text-[11px]">
              Native Windows MediaFoundation audio loopback and multimonitor screen capture with zero disk I/O.
            </p>
            <div className="text-teal-400 font-mono text-[10px]">License: BSD-3-Clause / MIT</div>
          </div>
        </div>
      </div>

      {/* Security & Vulnerability Policy */}
      <div className="p-6 rounded-2xl border border-border bg-panel space-y-3">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-400" />
          Responsible Vulnerability Disclosure
        </h2>
        <p className="text-xs text-gray-400 leading-relaxed">
          Security is fundamental to Trustwire. If you discover a vulnerability or security flaw, please report it privately via
          the instructions in <code className="bg-surface px-1.5 py-0.5 rounded text-teal-300 font-mono">SECURITY.md</code>.
          Never disclose vulnerabilities publicly prior to a coordinated patch.
        </p>
      </div>

      {/* Probabilistic Disclaimer */}
      <div className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/5 text-xs text-amber-200/90 leading-relaxed">
        <strong>Forensic Advisory Disclaimer:</strong> Trustwire outputs are probabilistic risk metrics and evidence indicators.
        They do not constitute legal proof or certified judicial verification. Always verify critical requests via out-of-band channels.
      </div>
    </div>
  );
};

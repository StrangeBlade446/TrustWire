import React, { useEffect, useState } from 'react';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
  Layers,
  Zap,
  Shield,
  FileCheck,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { ModelInfo } from '../types';

export const ModelsPerformance: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchModels = async () => {
    try {
      const data = await api.getModels();
      setModels(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <Cpu className="w-6 h-6 text-teal-400" />
            Detector Architecture & Model Benchmarks
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Verified local machine-learning checkpoints, execution runtimes, input requirements, and forensic limitations.
          </p>
        </div>

        <button
          onClick={fetchModels}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface border border-border hover:border-teal-500/50 text-xs text-gray-300 transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Model Status
        </button>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {models.map((model) => (
          <div
            key={model.id}
            className="p-6 rounded-2xl border border-border bg-panel space-y-5 hover:border-border-focus transition-all"
          >
            {/* Header of Card */}
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-1">
                <span className="text-[11px] font-mono text-teal-400 uppercase tracking-wider">
                  v{model.version} • {model.license}
                </span>
                <h3 className="text-base font-bold text-white">{model.name}</h3>
                <p className="text-xs text-gray-400 font-mono truncate">{model.source}</p>
              </div>

              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 ${
                model.status === 'Ready'
                  ? 'bg-teal-500/10 text-teal-300 border border-teal-500/20'
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
              }`}>
                {model.status === 'Ready' ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
                    Ready
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                    Unavailable
                  </>
                )}
              </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-surface p-4 rounded-xl border border-border/60">
              <div>
                <span className="text-gray-500 block text-[11px]">Execution Hardware</span>
                <span className="font-medium text-gray-200">{model.device}</span>
              </div>
              <div>
                <span className="text-gray-500 block text-[11px]">Measured Latency</span>
                <span className="font-mono text-teal-300 font-semibold">{model.measured_inference_ms.toFixed(1)} ms</span>
              </div>
              <div className="col-span-2 pt-2 border-t border-border/40">
                <span className="text-gray-500 block text-[11px]">Input Pipeline Requirements</span>
                <span className="text-gray-300 text-[11px]">{model.input_requirements}</span>
              </div>
            </div>

            {/* Forensic Limitations & Disclosure */}
            <div className="p-3 rounded-xl bg-background/50 border border-border/40 text-xs text-gray-400 space-y-1">
              <span className="font-semibold text-gray-300 block flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5 text-cyan-400" />
                Forensic Decision Boundaries & Limitations:
              </span>
              <p className="text-[11px] leading-relaxed">
                {model.limitations}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Honest Results Notice */}
      <div className="p-6 rounded-2xl border border-border bg-panel space-y-3">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Shield className="w-4 h-4 text-teal-400" />
          Probabilistic Integrity & Zero Fabrication Guarantee
        </h3>
        <p className="text-xs text-gray-400 leading-relaxed">
          Trustwire adheres to strict honest disclosure. Deepfake and synthetic voice detection are statistical forensic techniques, not absolute mathematical proofs.
          No confidence scores are simulated, and "No suspicious evidence detected" does not guarantee authenticity.
          All models run strictly on local CPU/hardware using verified weights; unverified models are marked Unavailable.
        </p>
      </div>
    </div>
  );
};

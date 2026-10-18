import React, { useEffect, useState } from 'react';
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  Video,
  Mic,
  Activity,
  HardDrive,
  Clock,
  ArrowRight,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  Layers
} from 'lucide-react';
import { api } from '../services/api';
import { MonitoringStatus, AlertItem, ModelInfo, PrivacyStatus } from '../types';

interface DashboardProps {
  onNavigate: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [monitoring, setMonitoring] = useState<MonitoringStatus | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [privacy, setPrivacy] = useState<PrivacyStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setError(null);
      const [monData, alertData, modelData, privData] = await Promise.all([
        api.getMonitoringStatus(),
        api.getAlerts({ include_dismissed: false }),
        api.getModels(),
        api.getPrivacyStatus()
      ]);
      setMonitoring(monData);
      setAlerts(alertData.slice(0, 4));
      setModels(modelData);
      setPrivacy(privData);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to Trustwire backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'Critical':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">Critical</span>;
      case 'High':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">High</span>;
      case 'Caution':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">Caution</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">Informational</span>;
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">Security Command Dashboard</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-500/10 text-teal-300 border border-teal-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
              Windows Core Active
            </span>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            Real-time visual forensics and synthetic voice discrimination via on-device AI models.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('monitoring')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              monitoring?.is_monitoring
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20'
                : 'bg-teal-500 text-black hover:bg-teal-400 font-semibold shadow-lg shadow-teal-500/20'
            }`}
          >
            <Activity className="w-4 h-4" />
            {monitoring?.is_monitoring ? 'Monitoring Live — View Stream' : 'Launch Live Monitoring'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center gap-3 text-rose-300 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Grid of Key System Telemetry */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Monitoring State */}
        <div className="bg-panel border border-border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium uppercase tracking-wider">
            <span>Live Shield</span>
            <Activity className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl font-bold text-white flex items-center gap-2">
            {monitoring?.is_monitoring ? (
              <span className="text-teal-400 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-pulse" />
                Active
              </span>
            ) : (
              <span className="text-gray-400 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-gray-500" />
                Standby
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400">
            {monitoring?.is_monitoring ? `Scanning ${monitoring.screen_source?.name || 'Screen'} & Loopback` : 'Zero background CPU usage while stopped'}
          </p>
        </div>

        {/* Video Forensics Status */}
        <div className="bg-panel border border-border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium uppercase tracking-wider">
            <span>Video Deepfake Engine</span>
            <Video className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {models.find(m => m.id === 'video_deepfake')?.status === 'Ready' ? (
              <span className="text-teal-400">Ready</span>
            ) : (
              <span className="text-gray-400">Unavailable</span>
            )}
          </div>
          <p className="text-xs text-gray-400 truncate">
            ViT Facial Forensics ONNX (205ms/frame)
          </p>
        </div>

        {/* Audio Forensics Status */}
        <div className="bg-panel border border-border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium uppercase tracking-wider">
            <span>Audio Voice Classifier</span>
            <Mic className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {models.find(m => m.id === 'audio_deepfake')?.status === 'Ready' ? (
              <span className="text-teal-400">Ready</span>
            ) : (
              <span className="text-gray-400">Unavailable</span>
            )}
          </div>
          <p className="text-xs text-gray-400 truncate">
            Wav2Vec2 Spoofing Model (287ms/chunk)
          </p>
        </div>

        {/* Privacy & Retention Status */}
        <div className="bg-panel border border-border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400 text-xs font-medium uppercase tracking-wider">
            <span>Privacy Policy</span>
            <HardDrive className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl font-bold text-teal-400">
            15m Max
          </div>
          <p className="text-xs text-gray-400">
            {privacy?.active_temp_files || 0} active temp files ({privacy?.total_temp_size_mb || 0} MB)
          </p>
        </div>
      </div>

      {/* Main Center Content: Recent Alerts & Quick Forensics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Recent Alerts Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-amber-400" />
              Recent High-Confidence Alerts
            </h2>
            <button
              onClick={() => onNavigate('alerts')}
              className="text-xs text-teal-400 hover:text-teal-300 flex items-center gap-1 font-medium"
            >
              View Full History <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {alerts.length === 0 ? (
              <div className="p-8 border border-border bg-panel/50 rounded-xl text-center space-y-3">
                <ShieldCheck className="w-10 h-10 text-teal-400/60 mx-auto" />
                <p className="text-sm font-medium text-gray-300">No Active Threats or High-Risk Alerts</p>
                <p className="text-xs text-gray-500 max-w-sm mx-auto">
                  All systems operating normally. In-session analysis will surface suspicious speech or frame manipulations immediately.
                </p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="p-4 rounded-xl border border-border bg-panel hover:border-border-focus transition-all space-y-2"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        {getSeverityBadge(alert.severity)}
                        <span className="text-xs text-gray-400 font-mono">{alert.created_at_iso}</span>
                        <span className="text-xs text-gray-500">• {alert.source}</span>
                      </div>
                      <h3 className="text-sm font-semibold text-white">{alert.title}</h3>
                    </div>
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-surface border border-border text-teal-300">
                      {(alert.confidence_score * 100).toFixed(0)}% Conf
                    </span>
                  </div>
                  <p className="text-xs text-gray-300">{alert.explanation}</p>
                  <div className="p-2.5 rounded bg-surface/60 border border-border/60 text-xs text-amber-300/90 font-medium">
                    Recommended Action: {alert.suggested_action}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Live Telemetry & Fast Media Analysis Launcher */}
        <div className="space-y-6">
          {/* Quick File Analysis Card */}
          <div className="p-6 rounded-xl border border-border bg-panel space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-teal-400" />
              Inspect Media File
            </h3>
            <p className="text-xs text-gray-400">
              Upload a recorded video (MP4, MKV, WebM) or audio file (WAV, MP3) to run deepfake detection without enabling live screen capture.
            </p>
            <button
              onClick={() => onNavigate('analyze')}
              className="w-full py-2.5 rounded-lg bg-surface border border-border hover:border-teal-500/50 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all"
            >
              Open Media Analyzer <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Model Status Summary Card */}
          <div className="p-6 rounded-xl border border-border bg-panel space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Shield className="w-4 h-4 text-cyan-400" />
              Verified Local Models
            </h3>
            <div className="space-y-3 text-xs">
              {models.map(m => (
                <div key={m.id} className="flex items-center justify-between pb-2 border-b border-border/40 last:border-0 last:pb-0">
                  <div className="space-y-0.5">
                    <div className="font-medium text-white">{m.name}</div>
                    <div className="text-[11px] text-gray-400">{m.device}</div>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                    m.status === 'Ready'
                      ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
                      : 'bg-gray-500/10 text-gray-400 border border-gray-500/20'
                  }`}>
                    {m.status}
                  </span>
                </div>
              ))}
            </div>
            <button
              onClick={() => onNavigate('models')}
              className="text-xs text-gray-400 hover:text-white flex items-center gap-1 font-medium pt-1"
            >
              Model Benchmarks & Limits <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import {
  Play,
  Square,
  Video,
  Mic,
  Activity,
  AlertTriangle,
  Monitor,
  Volume2,
  CheckCircle2,
  Settings,
  Cpu,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';
import { MonitoringStatus, CaptureSources, AlertItem } from '../types';

interface LiveMonitoringProps {
  currentStatus?: MonitoringStatus | null;
  onStatusChange?: (s: MonitoringStatus | null) => void;
}

export const LiveMonitoring: React.FC<LiveMonitoringProps> = ({ currentStatus, onStatusChange }) => {
  const [status, setStatus] = useState<MonitoringStatus | null>(currentStatus || null);
  const [sources, setSources] = useState<CaptureSources | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // User configuration toggles
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [selectedMonitor, setSelectedMonitor] = useState<number>(1);
  const [selectedAudioDevice, setSelectedAudioDevice] = useState<string>('');

  useEffect(() => {
    if (currentStatus) {
      setStatus(currentStatus);
    }
  }, [currentStatus]);

  const fetchStatusAndAlerts = async () => {
    try {
      const [monData, alertData] = await Promise.all([
        api.getMonitoringStatus(),
        api.getAlerts({ include_dismissed: false })
      ]);
      setStatus(monData);
      if (onStatusChange) onStatusChange(monData);
      setAlerts(alertData.filter(a => a.source === 'Live Monitoring').slice(0, 10));
    } catch (e: any) {
      console.error(e);
    }
  };

  useEffect(() => {
    // Initial fetch of capture sources
    api.getMonitoringSources()
      .then(src => {
        setSources(src);
        if (src.monitors.length > 0) setSelectedMonitor(src.monitors[0].index);
        if (src.audio_loopback_devices.length > 0) setSelectedAudioDevice(src.audio_loopback_devices[0].id);
      })
      .catch(e => setError("Failed to enumerate capture hardware."));

    fetchStatusAndAlerts();
    const interval = setInterval(fetchStatusAndAlerts, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleMonitoring = async () => {
    setLoading(true);
    setError(null);
    try {
      if (status?.is_monitoring) {
        await api.stopMonitoring();
      } else {
        await api.startMonitoring({
          video_enabled: videoEnabled,
          audio_enabled: audioEnabled,
          monitor_index: selectedMonitor,
          audio_device_id: selectedAudioDevice || undefined
        });
      }
      const updated = await api.getMonitoringStatus();
      setStatus(updated);
      if (onStatusChange) onStatusChange(updated);
      await fetchStatusAndAlerts();
    } catch (err: any) {
      setError(err.message || 'Operation failed.');
    } finally {
      setLoading(false);
    }
  };

  const videoAlerts = alerts.filter(a => a.category === 'video_deepfake');
  const audioAlerts = alerts.filter(a => a.category === 'audio_deepfake');

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header and Master Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-border">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            Live System Monitoring
            {status?.is_monitoring && (
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                Live Analysis Running
              </span>
            )}
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Real-time inspection of active desktop screen regions and system WASAPI playback audio.
          </p>
        </div>

        <button
          onClick={handleToggleMonitoring}
          disabled={loading}
          className={`flex items-center gap-3 px-6 py-3 rounded-xl font-semibold text-sm transition-all shadow-lg ${
            status?.is_monitoring
              ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/20'
              : 'bg-teal-500 hover:bg-teal-400 text-black shadow-teal-500/20'
          }`}
        >
          {status?.is_monitoring ? (
            <>
              <Square className="w-5 h-5 fill-current" />
              <span>Stop Active Capture</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5 fill-current" />
              <span>Start Live Monitoring</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center gap-3 text-rose-300 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Capture Disclosure & Privacy Guarantee Notice */}
      <div className="p-4 rounded-xl border border-teal-500/20 bg-teal-500/5 text-xs text-teal-200/90 flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-teal-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="font-semibold text-teal-300">Privacy & Hardware Disclosure:</span>
          <p className="text-gray-400 leading-relaxed">
            Trustwire monitors only the selected display and speaker loopback playback. The webcam and microphone are never accessed.
            Frames and audio buffers are processed entirely in memory in real-time, zero continuous recording to disk, and strict 15-minute maximum retention on diagnostic samples.
          </p>
        </div>
      </div>

      {/* Control Configuration Panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Video Channel Toggle */}
        <div className={`p-5 rounded-xl border transition-all ${
          videoEnabled ? 'border-border bg-panel' : 'border-border/40 bg-surface/40 opacity-70'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <Video className="w-5 h-5 text-teal-400" />
              <span className="font-semibold text-sm text-white">Video Deepfake Stream</span>
            </div>
            <input
              type="checkbox"
              checked={videoEnabled}
              disabled={status?.is_monitoring}
              onChange={(e) => setVideoEnabled(e.target.checked)}
              className="w-4 h-4 rounded text-teal-500 focus:ring-teal-400 border-border bg-surface cursor-pointer"
            />
          </div>
          <div className="space-y-3 text-xs">
            <div>
              <label className="text-gray-400 block mb-1">Target Display Source</label>
              <select
                disabled={status?.is_monitoring}
                value={selectedMonitor}
                onChange={(e) => setSelectedMonitor(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg px-3 py-1.5 text-gray-200 text-xs focus:outline-none focus:border-teal-500"
              >
                {sources?.monitors.map(m => (
                  <option key={m.index} value={m.index}>{m.name} ({m.width}x{m.height})</option>
                ))}
              </select>
            </div>
            <div className="flex justify-between text-gray-400 pt-2 border-t border-border/40">
              <span>Processed Frames:</span>
              <span className="font-mono text-white">{status?.video_frames_processed || 0}</span>
            </div>
          </div>
        </div>

        {/* Audio Channel Toggle */}
        <div className={`p-5 rounded-xl border transition-all ${
          audioEnabled ? 'border-border bg-panel' : 'border-border/40 bg-surface/40 opacity-70'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <Mic className="w-5 h-5 text-cyan-400" />
              <span className="font-semibold text-sm text-white">Audio Voice Cloning</span>
            </div>
            <input
              type="checkbox"
              checked={audioEnabled}
              disabled={status?.is_monitoring}
              onChange={(e) => setAudioEnabled(e.target.checked)}
              className="w-4 h-4 rounded text-teal-500 focus:ring-teal-400 border-border bg-surface cursor-pointer"
            />
          </div>
          <div className="space-y-3 text-xs">
            <div>
              <label className="text-gray-400 block mb-1">WASAPI Loopback Device</label>
              <select
                disabled={status?.is_monitoring}
                value={selectedAudioDevice}
                onChange={(e) => setSelectedAudioDevice(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3 py-1.5 text-gray-200 text-xs focus:outline-none focus:border-teal-500 truncate"
              >
                {sources?.audio_loopback_devices.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div className="flex justify-between text-gray-400 pt-2 border-t border-border/40">
              <span>Acoustic Chunks:</span>
              <span className="font-mono text-white">{status?.audio_chunks_processed || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Activity Telemetry Strip */}
      {status?.is_monitoring && (
        <div className="p-4 rounded-xl border border-border bg-panel flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
          <div className="flex items-center gap-2 text-teal-400">
            <Activity className="w-4 h-4 animate-spin" />
            <span>PIPELINE ACTIVE</span>
          </div>
          <div className="text-gray-300">
            Last Video Score: <span className="text-white">{(status.recent_activity.last_video_score * 100).toFixed(1)}%</span>
          </div>
          <div className="text-gray-300">
            Last Audio Fake Score: <span className="text-white">{(status.recent_activity.last_audio_score * 100).toFixed(1)}%</span>
          </div>
        </div>
      )}

      {/* 2-Column Parallel Live Alert Feeds */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-teal-400" />
          Live Forensic Alert Streams
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Video Alert Stream */}
          <div className="p-5 rounded-xl border border-border bg-panel space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <span className="font-semibold text-xs text-gray-300 flex items-center gap-2">
                <Video className="w-4 h-4 text-teal-400" />
                Screen Video Detections
              </span>
              <span className="text-xs font-mono text-gray-400">{videoAlerts.length}</span>
            </div>
            <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
              {videoAlerts.length === 0 ? (
                <div className="p-6 text-center text-xs text-gray-500">No manipulated video artifacts detected.</div>
              ) : (
                videoAlerts.map(a => (
                  <div key={a.id} className="p-3 rounded-lg bg-surface border border-border space-y-1.5 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-rose-400">{a.severity}</span>
                      <span className="text-gray-500 font-mono text-[10px]">{a.created_at_iso.split(' ')[1]}</span>
                    </div>
                    <p className="text-gray-300">{a.title}</p>
                    <div className="text-[11px] text-teal-300 font-mono">Confidence: {(a.confidence_score * 100).toFixed(0)}%</div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Audio Alert Stream */}
          <div className="p-5 rounded-xl border border-border bg-panel space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <span className="font-semibold text-xs text-gray-300 flex items-center gap-2">
                <Mic className="w-4 h-4 text-cyan-400" />
                Voice Cloning Detections
              </span>
              <span className="text-xs font-mono text-gray-400">{audioAlerts.length}</span>
            </div>
            <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
              {audioAlerts.length === 0 ? (
                <div className="p-6 text-center text-xs text-gray-500">No synthetic voice artifacts detected.</div>
              ) : (
                audioAlerts.map(a => (
                  <div key={a.id} className="p-3 rounded-lg bg-surface border border-border space-y-1.5 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-rose-400">{a.severity}</span>
                      <span className="text-gray-500 font-mono text-[10px]">{a.created_at_iso.split(' ')[1]}</span>
                    </div>
                    <p className="text-gray-300">{a.title}</p>
                    <div className="text-[11px] text-cyan-300 font-mono">Confidence: {(a.confidence_score * 100).toFixed(0)}%</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

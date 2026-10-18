import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  Square,
  Shield,
  Activity,
  Maximize2
} from 'lucide-react';
import { api } from '../services/api';
import { MonitoringStatus } from '../types';

interface LiveMonitoringOverlayProps {
  monitoringStatus: MonitoringStatus | null;
  onStatusChange?: (status: MonitoringStatus | null) => void;
  onNavigateToMonitoring?: () => void;
}

export const LiveMonitoringOverlay: React.FC<LiveMonitoringOverlayProps> = ({
  monitoringStatus,
  onStatusChange,
  onNavigateToMonitoring
}) => {
  const [isPaused, setIsPaused] = useState(false);
  const [loading, setLoading] = useState(false);

  const isMonitoring = Boolean(monitoringStatus?.is_monitoring) || isPaused;

  // Sync state to native Electron overlay window
  useEffect(() => {
    const desktop = (window as any).trustwireDesktop;
    if (desktop?.sendMonitoringState) {
      desktop.sendMonitoringState({
        is_monitoring: isMonitoring,
        isPaused: isPaused,
        stats: isPaused
          ? 'Analysis Suspended'
          : `Frames: ${monitoringStatus?.video_frames_processed || 0} • Audio: ${monitoringStatus?.audio_chunks_processed || 0}`
      });
    }
  }, [isMonitoring, isPaused, monitoringStatus?.video_frames_processed, monitoringStatus?.audio_chunks_processed]);

  // Handle remote control commands from native Electron overlay
  useEffect(() => {
    const desktop = (window as any).trustwireDesktop;
    if (desktop?.onRemoteControl) {
      const unsubscribe = desktop.onRemoteControl(async (action: string) => {
        if (action === 'stop') {
          handleStop();
        } else if (action === 'pause') {
          handlePause();
        } else if (action === 'play') {
          handleResume();
        }
      });
      return unsubscribe;
    }
  }, [isPaused]);

  const handlePause = async () => {
    setLoading(true);
    try {
      await api.stopMonitoring();
      setIsPaused(true);
      const updated = await api.getMonitoringStatus();
      if (onStatusChange) onStatusChange(updated);
    } catch (e) {
      console.error('Failed to pause monitoring:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleResume = async () => {
    setLoading(true);
    try {
      await api.startMonitoring({
        video_enabled: true,
        audio_enabled: true,
        monitor_index: 1
      });
      setIsPaused(false);
      const updated = await api.getMonitoringStatus();
      if (onStatusChange) onStatusChange(updated);
    } catch (e) {
      console.error('Failed to resume monitoring:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await api.stopMonitoring();
      setIsPaused(false);
      const updated = await api.getMonitoringStatus();
      if (onStatusChange) onStatusChange(updated);
      const desktop = (window as any).trustwireDesktop;
      if (desktop?.sendMonitoringState) {
        desktop.sendMonitoringState({ is_monitoring: false });
      }
    } catch (e) {
      console.error('Failed to stop monitoring:', e);
    } finally {
      setLoading(false);
    }
  };

  if (!isMonitoring) {
    return null;
  }

  return (
    <div className="fixed top-3 left-1/2 -translate-x-1/2 z-50 animate-in fade-in slide-in-from-top-4 duration-300">
      <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-[#0B0D10]/95 backdrop-blur-xl border border-white/15 shadow-2xl shadow-black/80">
        {/* Brand & Status Indicator */}
        <div
          onClick={onNavigateToMonitoring}
          className="flex items-center gap-2.5 cursor-pointer hover:opacity-80 transition-opacity pr-2 border-r border-white/10"
          title="Open Live Monitoring View"
        >
          <div className="p-1 rounded-full bg-teal-500/10 text-teal-400">
            <Shield className="w-3.5 h-3.5" />
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isPaused
                  ? 'bg-amber-400 shadow-[0_0_8px_#FBBF24]'
                  : 'bg-teal-400 animate-pulse shadow-[0_0_8px_#2DD4BF]'
              }`}
            />
            <span className="text-xs font-bold text-white tracking-wide font-mono uppercase">
              {isPaused ? 'Paused' : 'Monitoring'}
            </span>
          </div>
        </div>

        {/* Real-time stats ticker */}
        <div className="hidden sm:flex items-center gap-2 text-[11px] font-mono text-gray-400 pr-2 border-r border-white/10">
          <Activity className="w-3 h-3 text-teal-400 animate-pulse" />
          <span>
            {isPaused
              ? 'Capture Suspended'
              : `Frames: ${monitoringStatus?.video_frames_processed || 0} • Chunks: ${monitoringStatus?.audio_chunks_processed || 0}`}
          </span>
        </div>

        {/* Action Controls: Pause / Play & Stop */}
        <div className="flex items-center gap-2">
          {isPaused ? (
            <button
              onClick={handleResume}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 border border-teal-500/40 transition-all shadow-sm"
              title="Resume Live Monitoring"
            >
              <Play className="w-3 h-3 fill-current" />
              <span>Resume</span>
            </button>
          ) : (
            <button
              onClick={handlePause}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 hover:bg-amber-500/20 text-gray-200 hover:text-amber-300 border border-white/15 hover:border-amber-500/30 transition-all shadow-sm"
              title="Pause Live Monitoring"
            >
              <Pause className="w-3 h-3 fill-current" />
              <span>Pause</span>
            </button>
          )}

          <button
            onClick={handleStop}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white shadow-sm shadow-rose-600/30 transition-all"
            title="Stop Live Monitoring"
          >
            <Square className="w-3 h-3 fill-current" />
            <span>Stop</span>
          </button>

          {onNavigateToMonitoring && (
            <button
              onClick={onNavigateToMonitoring}
              className="p-1 rounded-full bg-white/5 hover:bg-white/15 text-gray-400 hover:text-white transition-colors ml-1"
              title="Focus Live Monitoring Dashboard"
            >
              <Maximize2 className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

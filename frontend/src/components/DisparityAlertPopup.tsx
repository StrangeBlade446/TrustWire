import React, { useEffect } from 'react';
import {
  FileVideo,
  FileAudio,
  AlertTriangle,
  X,
  Pause,
  ExternalLink,
  CheckCircle2,
  AlertOctagon,
  ShieldAlert
} from 'lucide-react';
import { AlertItem } from '../types';

interface DisparityAlertPopupProps {
  alert: AlertItem | null;
  onDismiss: () => void;
  onPauseMonitoring?: () => void;
  onViewAlertHistory?: () => void;
}

export const DisparityAlertPopup: React.FC<DisparityAlertPopupProps> = ({
  alert,
  onDismiss,
  onPauseMonitoring,
  onViewAlertHistory
}) => {
  // Auto-dismiss after 12 seconds
  useEffect(() => {
    if (!alert) return;

    const timer = setTimeout(() => {
      onDismiss();
    }, 12000);

    // Optional audio chime on alert arrival
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        const ctx = new AudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
        osc.frequency.exponentialRampToValueAtTime(880.0, ctx.currentTime + 0.14); // A5
        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.45);
        osc.start();
        osc.stop(ctx.currentTime + 0.5);
      }
    } catch (e) {}

    return () => clearTimeout(timer);
  }, [alert?.id, onDismiss]);

  if (!alert) return null;

  const isVideoDisparity = alert.category === 'video_deepfake';

  const disparityConfig = isVideoDisparity
    ? {
        tagText: 'VISUAL DISPARITY · 1 OF 2',
        title: 'Visual / Deepfake Video Disparity',
        borderClass: 'border-rose-500/40 hover:border-rose-500/60',
        badgeClass: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
        glowClass: 'shadow-[0_12px_40px_rgba(244,63,94,0.22)]',
        accentText: 'text-rose-400',
        Icon: FileVideo,
      }
    : {
        tagText: 'ACOUSTIC DISPARITY · 2 OF 2',
        title: 'Acoustic / Synthetic Speech Disparity',
        borderClass: 'border-cyan-500/40 hover:border-cyan-500/60',
        badgeClass: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
        glowClass: 'shadow-[0_12px_40px_rgba(6,182,212,0.22)]',
        accentText: 'text-cyan-400',
        Icon: FileAudio,
      };

  const { tagText, title, borderClass, badgeClass, glowClass, accentText, Icon } = disparityConfig;

  return (
    <div className="fixed top-4 right-4 z-50 w-full max-w-md animate-in slide-in-from-top-3 fade-in duration-200 pointer-events-auto">
      <div
        className={`rounded-xl bg-[#151a20]/95 backdrop-blur-xl border ${borderClass} ${glowClass} p-4 space-y-3 transition-all`}
        role="alert"
      >
        {/* Top Header Bar */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${badgeClass}`}>
              {tagText}
            </span>
            <span className="text-[11px] font-mono text-gray-400">
              {Math.round((alert.confidence_score || 0) * 100)}% Confidence
            </span>
          </div>

          <button
            onClick={onDismiss}
            className="p-1 rounded-md text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            title="Dismiss Alert"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Title and Icon */}
        <div className="flex items-start gap-2.5">
          <div className={`p-2 rounded-lg bg-surface border border-white/10 ${accentText} mt-0.5 flex-shrink-0`}>
            <Icon className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight leading-snug">
              {alert.title}
            </h3>
            <p className="text-xs text-gray-300 mt-1 leading-relaxed">
              {alert.explanation}
            </p>
          </div>
        </div>

        {/* Action Recommendation Banner */}
        <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200/90 flex items-start gap-2">
          <AlertOctagon className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="leading-tight">
            <span className="font-semibold text-white">Recommended Action: </span>
            {alert.suggested_action}
          </div>
        </div>

        {/* Bottom Actions Row */}
        <div className="flex items-center justify-between gap-2 pt-1">
          {onPauseMonitoring && (
            <button
              onClick={() => {
                onPauseMonitoring();
                onDismiss();
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/5 hover:bg-amber-500/20 text-gray-300 hover:text-amber-300 border border-white/10 transition-colors"
            >
              <Pause className="w-3 h-3" />
              <span>Pause</span>
            </button>
          )}

          <div className="flex items-center gap-2 ml-auto">
            {onViewAlertHistory && (
              <button
                onClick={() => {
                  onViewAlertHistory();
                  onDismiss();
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-surface hover:bg-panel text-gray-300 hover:text-white border border-border transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
                <span>History</span>
              </button>
            )}

            <button
              onClick={onDismiss}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-semibold bg-teal-500 hover:bg-teal-400 text-black shadow-md shadow-teal-500/20 transition-all"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Acknowledge</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

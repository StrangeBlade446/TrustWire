import React, { useEffect } from 'react';
import {
  FileVideo,
  FileAudio,
  AlertTriangle,
  X,
  Pause,
  ExternalLink,
  CheckCircle2,
  AlertOctagon
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
  useEffect(() => {
    if (!alert) return;

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
  }, [alert?.id]);

  if (!alert) return null;

  // Determine which of the 2 disparities was detected
  const isVideoDisparity = alert.category === 'video_deepfake';
  const isAudioDisparity = alert.category === 'audio_deepfake';

  const disparityConfig = isVideoDisparity
    ? {
        typeNumber: 'DISPARITY 1 OF 2',
        typeName: 'Visual / Deepfake Video Disparity',
        typeSubtitle: 'Facial Tampering or Synthetic Generative Artifacts Detected',
        themeBorder: 'border-rose-500/50',
        themeBg: 'bg-rose-500/10',
        themeBadge: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
        themeGlow: 'shadow-rose-950/60',
        Icon: FileVideo,
        iconColor: 'text-rose-400'
      }
    : {
        typeNumber: 'DISPARITY 2 OF 2',
        typeName: 'Acoustic / Synthetic Audio Disparity',
        typeSubtitle: 'Voice Cloning or Neural Speech Spoofing Detected in Playback',
        themeBorder: 'border-cyan-500/50',
        themeBg: 'bg-cyan-500/10',
        themeBadge: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
        themeGlow: 'shadow-cyan-950/60',
        Icon: FileAudio,
        iconColor: 'text-cyan-400'
      };

  const { typeNumber, typeName, typeSubtitle, themeBorder, themeBadge, themeGlow, Icon, iconColor } = disparityConfig;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className={`w-full max-w-lg rounded-2xl bg-[#0F1216] border ${themeBorder} shadow-2xl ${themeGlow} p-6 space-y-5 animate-in zoom-in-95 duration-200`}
        role="alertdialog"
        aria-modal="true"
      >
        {/* Header: Disparity Identification & Close Button */}
        <div className="flex items-start justify-between gap-3 pb-3 border-b border-border/60">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl bg-surface border border-white/10 ${iconColor} shadow-inner`}>
              <Icon className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${themeBadge}`}>
                  {typeNumber}
                </span>
                <span className="text-xs font-mono text-gray-400">
                  {(alert.confidence_score * 100).toFixed(0)}% Confidence
                </span>
              </div>
              <h2 className="text-base font-bold text-white tracking-tight mt-0.5">
                {typeName}
              </h2>
            </div>
          </div>

          <button
            onClick={onDismiss}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface transition-colors"
            title="Dismiss Alert"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Observation Subtitle */}
        <div className="text-xs text-gray-400 font-medium">
          {typeSubtitle}
        </div>

        {/* Forensic Disparity Details */}
        <div className="space-y-3 p-4 rounded-xl bg-surface/80 border border-border text-xs leading-relaxed">
          <div className="font-semibold text-white flex items-center gap-2">
            <AlertTriangle className={`w-4 h-4 ${iconColor}`} />
            <span>{alert.title}</span>
          </div>

          <p className="text-gray-300">
            {alert.explanation}
          </p>

          {/* Triggering Evidence if present */}
          {alert.evidence && alert.evidence.fake_score !== undefined && (
            <div className="pt-2 border-t border-border/50 text-[11px] font-mono text-gray-400 space-y-1">
              <div>
                <span className="text-gray-400 font-semibold">Forensic Disparity Score: </span>
                <span className="text-white">{(alert.evidence.fake_score * 100).toFixed(1)}%</span>
              </div>
            </div>
          )}
        </div>

        {/* Recommended Action Pill */}
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-2.5">
          <AlertOctagon className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="block text-white font-medium mb-0.5">Recommended Protective Action:</strong>
            {alert.suggested_action}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          {onPauseMonitoring ? (
            <button
              onClick={() => {
                onPauseMonitoring();
                onDismiss();
              }}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-white/10 hover:bg-amber-500/20 text-gray-200 hover:text-amber-300 border border-white/15 transition-all"
            >
              <Pause className="w-3.5 h-3.5" />
              <span>Pause Monitoring</span>
            </button>
          ) : <div />}

          <div className="flex items-center gap-2 w-full sm:w-auto">
            {onViewAlertHistory && (
              <button
                onClick={() => {
                  onViewAlertHistory();
                  onDismiss();
                }}
                className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-surface hover:bg-panel text-gray-300 hover:text-white border border-border transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Alert History</span>
              </button>
            )}

            <button
              onClick={onDismiss}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-5 py-2 rounded-xl text-xs font-semibold bg-teal-500 hover:bg-teal-400 text-black shadow-lg shadow-teal-500/20 transition-all"
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

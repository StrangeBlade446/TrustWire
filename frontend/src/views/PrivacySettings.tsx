import React, { useEffect, useState } from 'react';
import {
  HardDrive,
  Trash2,
  Lock,
  EyeOff,
  Clock,
  Shield,
  Key,
  CheckCircle2,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { api, getApiToken, setApiToken } from '../services/api';
import { PrivacyStatus } from '../types';

export const PrivacySettings: React.FC = () => {
  const [privacy, setPrivacy] = useState<PrivacyStatus | null>(null);
  const [tokenInput, setTokenInput] = useState(getApiToken());
  const [purging, setPurging] = useState(false);
  const [savedNotice, setSavedNotice] = useState(false);

  const fetchPrivacy = async () => {
    try {
      const data = await api.getPrivacyStatus();
      setPrivacy(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchPrivacy();
    const interval = setInterval(fetchPrivacy, 4000);
    return () => clearInterval(interval);
  }, []);

  const handlePurge = async () => {
    setPurging(true);
    try {
      await api.purgePrivacyStorage();
      await fetchPrivacy();
    } catch (e) {
      console.error(e);
    } finally {
      setPurging(false);
    }
  };

  const handleSaveToken = () => {
    setApiToken(tokenInput);
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 2500);
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="pb-6 border-b border-border">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
          <Lock className="w-6 h-6 text-teal-400" />
          Privacy Guard & Retention Policy
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Enforce strict local-only inference, 15-minute maximum temporary data lifespan, and zero telemetry.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Retention Policy Box */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl border border-border bg-panel space-y-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Clock className="w-5 h-5 text-teal-400" />
                  Mandatory 15-Minute Data Lifespan Enforcement
                </h3>
                <p className="text-xs text-gray-400 mt-1">
                  Backend-enforced retention policy. Any diagnostic media artifacts automatically expire and are purged by background schedulers.
                </p>
              </div>

              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-teal-500/10 text-teal-300 border border-teal-500/20">
                Active Enforcer
              </span>
            </div>

            {/* Storage Metrics */}
            <div className="grid grid-cols-3 gap-4 text-xs bg-surface p-4 rounded-xl border border-border">
              <div>
                <span className="text-gray-400 block">Max Retention</span>
                <span className="text-base font-bold text-teal-400">15 Minutes</span>
              </div>
              <div>
                <span className="text-gray-400 block">Active Temp Files</span>
                <span className="text-base font-bold text-white">{privacy?.active_temp_files || 0}</span>
              </div>
              <div>
                <span className="text-gray-400 block">Temp Storage Volume</span>
                <span className="text-base font-bold text-white">{privacy?.total_temp_size_mb || 0} MB</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-gray-400 font-mono">
                Temp Directory: {privacy?.temp_directory || 'C:\\...\\temp_media'}
              </span>

              <button
                onClick={handlePurge}
                disabled={purging}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-semibold transition-all"
              >
                <Trash2 className="w-4 h-4" />
                {purging ? 'Purging...' : 'Purge All Temp Media Now'}
              </button>
            </div>
          </div>

          {/* Privacy Principles Card */}
          <div className="p-6 rounded-2xl border border-border bg-panel space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <EyeOff className="w-5 h-5 text-cyan-400" />
              Privacy & Zero-Transmission Architecture
            </h3>
            <ul className="space-y-2.5 text-xs text-gray-300">
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
                <span><strong>100% Local Inference:</strong> No audio recordings, video frames, or transcripts are ever transmitted to cloud servers.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
                <span><strong>No Raw Media in Alerts:</strong> Alert history persists only timestamped detection metadata and risk explanations, never raw clips.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
                <span><strong>Startup Crash Recovery:</strong> If the application terminates abnormally, leftover artifacts are automatically scrubbed on next launch.</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Security Capability Token Card */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl border border-border bg-panel space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Key className="w-4 h-4 text-amber-400" />
              Desktop Capability Token
            </h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Protects local API endpoints against unauthorized local processes or browser tabs. Verified with every request.
            </p>

            <div className="space-y-2">
              <input
                type="text"
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg p-2.5 text-xs font-mono text-gray-200 focus:outline-none focus:border-teal-500"
              />
              <button
                onClick={handleSaveToken}
                className="w-full py-2 rounded-lg bg-surface border border-border hover:border-teal-500/50 text-white text-xs font-semibold transition-all"
              >
                Save Capability Token
              </button>
            </div>

            {savedNotice && (
              <p className="text-xs text-teal-400 font-medium flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> Token updated in local session.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

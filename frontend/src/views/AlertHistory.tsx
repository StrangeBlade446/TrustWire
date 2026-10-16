import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  Search,
  Filter,
  Check,
  X,
  Trash2,
  Calendar,
  ExternalLink,
  Info,
  Clock,
  Layers
} from 'lucide-react';
import { api } from '../services/api';
import { AlertItem } from '../types';

export const AlertHistory: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [includeDismissed, setIncludeDismissed] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const data = await api.getAlerts({
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
        severity: severityFilter !== 'all' ? severityFilter : undefined,
        include_dismissed: includeDismissed
      });
      setAlerts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, [categoryFilter, severityFilter, includeDismissed]);

  const handleAcknowledge = async (id: string) => {
    await api.acknowledgeAlert(id);
    fetchAlerts();
  };

  const handleDismiss = async (id: string) => {
    await api.dismissAlert(id);
    fetchAlerts();
  };

  const handleClearAll = async () => {
    if (window.confirm("Are you sure you want to clear all stored alert metadata?")) {
      await api.clearAllAlerts();
      fetchAlerts();
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (!search) return true;
    const query = search.toLowerCase();
    return (
      a.title.toLowerCase().includes(query) ||
      a.explanation.toLowerCase().includes(query) ||
      a.source.toLowerCase().includes(query)
    );
  });

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-amber-400" />
            Alert History & Forensic Evidence
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Audit trail of suspicious visual manipulations, synthetic voice matches, and conversational social engineering patterns.
          </p>
        </div>

        <button
          onClick={handleClearAll}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface border border-border hover:border-rose-500/50 text-xs text-gray-400 hover:text-rose-400 transition-all"
        >
          <Trash2 className="w-4 h-4" />
          Clear Stored History
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl border border-border bg-panel flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search alerts by keywords, source, or explanation..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent text-xs text-white placeholder-gray-500 focus:outline-none w-full"
          />
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-surface border border-border rounded-lg px-2.5 py-1 text-gray-300 focus:outline-none focus:border-teal-500 text-xs"
            >
              <option value="all">All Categories</option>
              <option value="video_deepfake">Video Deepfake</option>
              <option value="audio_deepfake">Audio Deepfake</option>
              <option value="financial_fraud">Financial Fraud</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-surface border border-border rounded-lg px-2.5 py-1 text-gray-300 focus:outline-none focus:border-teal-500 text-xs"
            >
              <option value="all">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Caution">Caution</option>
              <option value="Informational">Informational</option>
            </select>
          </div>

          <label className="flex items-center gap-2 cursor-pointer text-gray-400">
            <input
              type="checkbox"
              checked={includeDismissed}
              onChange={(e) => setIncludeDismissed(e.target.checked)}
              className="w-3.5 h-3.5 rounded text-teal-500 border-border bg-surface"
            />
            <span>Include Dismissed</span>
          </label>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="p-12 text-center border border-border rounded-2xl bg-panel space-y-3">
            <Info className="w-8 h-8 text-gray-500 mx-auto" />
            <div className="text-sm font-semibold text-gray-300">No alerts matching filter criteria</div>
            <p className="text-xs text-gray-500">
              When suspicious frames, synthetic speech, or fraudulent patterns are detected, they are recorded here with forensic evidence.
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-6 rounded-2xl border transition-all space-y-3 ${
                alert.dismissed
                  ? 'border-border/40 bg-surface/30 opacity-60'
                  : 'border-border bg-panel hover:border-border-focus'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-0.5 rounded text-xs font-semibold ${
                    alert.severity === 'Critical'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : alert.severity === 'High'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : alert.severity === 'Caution'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  }`}>
                    {alert.severity}
                  </span>
                  <h3 className="text-sm font-semibold text-white">{alert.title}</h3>
                  {alert.repetition_count > 1 && (
                    <span className="px-2 py-0.5 rounded bg-surface border border-border text-[11px] text-teal-300 font-mono">
                      x{alert.repetition_count} repeats
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <span className="text-gray-400 font-mono">{alert.created_at_iso}</span>
                  <span className="text-gray-500">• {alert.source}</span>
                  <span className="px-2 py-0.5 rounded bg-surface border border-border text-teal-300 font-mono text-[11px]">
                    {(alert.confidence_score * 100).toFixed(0)}% Conf
                  </span>
                </div>
              </div>

              <p className="text-xs text-gray-300 leading-relaxed">
                {alert.explanation}
              </p>

              {/* Suggested Action Bar */}
              <div className="p-3 rounded-xl bg-surface border border-border text-xs text-amber-300 flex items-start justify-between gap-4">
                <div>
                  <span className="font-semibold block text-amber-200">Recommended Protective Action:</span>
                  <span>{alert.suggested_action}</span>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  {!alert.acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="px-2.5 py-1 rounded bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 text-teal-300 text-xs font-medium flex items-center gap-1"
                    >
                      <Check className="w-3.5 h-3.5" />
                      Acknowledge
                    </button>
                  )}
                  {!alert.dismissed && (
                    <button
                      onClick={() => handleDismiss(alert.id)}
                      className="px-2.5 py-1 rounded bg-surface hover:bg-border text-gray-400 hover:text-white text-xs font-medium flex items-center gap-1"
                    >
                      <X className="w-3.5 h-3.5" />
                      Dismiss
                    </button>
                  )}
                </div>
              </div>

              {/* Evidence Drawer */}
              {Object.keys(alert.evidence).length > 0 && (
                <div className="text-[11px] text-gray-400 font-mono bg-background/50 p-3 rounded-lg border border-border/40">
                  <span className="text-gray-500 uppercase tracking-wider block mb-1">Evidence Metadata:</span>
                  <pre className="overflow-x-auto whitespace-pre-wrap">{JSON.stringify(alert.evidence, null, 2)}</pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

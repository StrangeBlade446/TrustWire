import {
  AlertItem,
  ModelInfo,
  CaptureSources,
  MonitoringStatus,
  PrivacyStatus,
  MediaAnalysisResponse
} from '../types';

const API_BASE = 'http://127.0.0.1:8765';
let apiToken = localStorage.getItem('trustwire_token') || '';

export const setApiToken = (token: string) => {
  apiToken = token;
  localStorage.setItem('trustwire_token', token);
};

export const getApiToken = () => apiToken;

const getHeaders = (extraHeaders: Record<string, string> = {}) => {
  const headers: Record<string, string> = { ...extraHeaders };
  if (apiToken) {
    headers['X-Trustwire-Token'] = apiToken;
  }
  return headers;
};

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/api/health`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    const data = await res.json();
    if (data.api_token && !apiToken) {
      setApiToken(data.api_token);
    }
    return data;
  },

  async getModels(): Promise<ModelInfo[]> {
    const res = await fetch(`${API_BASE}/api/models`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch models: ${res.statusText}`);
    return res.json();
  },

  async getMonitoringSources(): Promise<CaptureSources> {
    const res = await fetch(`${API_BASE}/api/monitoring/sources`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch capture sources: ${res.statusText}`);
    return res.json();
  },

  async getMonitoringStatus(): Promise<MonitoringStatus> {
    const res = await fetch(`${API_BASE}/api/monitoring/status`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch monitoring status: ${res.statusText}`);
    return res.json();
  },

  async startMonitoring(params: {
    video_enabled: boolean;
    audio_enabled: boolean;
    monitor_index?: number;
    audio_device_id?: string;
  }) {
    const res = await fetch(`${API_BASE}/api/monitoring/start`, {
      method: 'POST',
      headers: getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error(`Failed to start monitoring: ${res.statusText}`);
    return res.json();
  },

  async stopMonitoring() {
    const res = await fetch(`${API_BASE}/api/monitoring/stop`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error(`Failed to stop monitoring: ${res.statusText}`);
    return res.json();
  },

  async uploadAndAnalyzeMedia(
    file: File,
    options: {
      analyze_video_track: boolean;
      analyze_audio_track: boolean;
    }
  ): Promise<MediaAnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('analyze_video_track', String(options.analyze_video_track));
    formData.append('analyze_audio_track', String(options.analyze_audio_track));

    const res = await fetch(`${API_BASE}/api/analyze/upload`, {
      method: 'POST',
      headers: getHeaders(),
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Upload analysis failed.');
    }
    return res.json();
  },

  async getAlerts(filters?: { category?: string; severity?: string; include_dismissed?: boolean }): Promise<AlertItem[]> {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.severity) params.append('severity', filters.severity);
    if (filters?.include_dismissed) params.append('include_dismissed', 'true');

    const res = await fetch(`${API_BASE}/api/alerts?${params.toString()}`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch alerts: ${res.statusText}`);
    return res.json();
  },

  async acknowledgeAlert(alertId: string) {
    const res = await fetch(`${API_BASE}/api/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      headers: getHeaders()
    });
    return res.json();
  },

  async dismissAlert(alertId: string) {
    const res = await fetch(`${API_BASE}/api/alerts/${alertId}/dismiss`, {
      method: 'POST',
      headers: getHeaders()
    });
    return res.json();
  },

  async clearAllAlerts() {
    const res = await fetch(`${API_BASE}/api/alerts`, {
      method: 'DELETE',
      headers: getHeaders()
    });
    return res.json();
  },

  async getPrivacyStatus(): Promise<PrivacyStatus> {
    const res = await fetch(`${API_BASE}/api/privacy/status`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch privacy status: ${res.statusText}`);
    return res.json();
  },

  async purgePrivacyStorage() {
    const res = await fetch(`${API_BASE}/api/privacy/purge`, {
      method: 'POST',
      headers: getHeaders()
    });
    return res.json();
  }
};

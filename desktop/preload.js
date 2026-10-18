/**
 * Trustwire Electron Preload Script
 * Provides secure context isolation bridge between native desktop shell and frontend.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('trustwireDesktop', {
  platform: process.platform,
  version: '1.0.0',
  isDesktop: true,
  apiBaseUrl: 'http://127.0.0.1:8765',
  sendMonitoringState: (state) => ipcRenderer.send('monitoring-state-changed', state),
  sendAlert: (alert) => ipcRenderer.send('disparity-alert', alert),
  dismissAlert: () => ipcRenderer.send('dismiss-overlay-alert'),
  onRemoteControl: (callback) => {
    const handler = (_event, action) => callback(action);
    ipcRenderer.on('remote-monitoring-control', handler);
    return () => ipcRenderer.removeListener('remote-monitoring-control', handler);
  }
});

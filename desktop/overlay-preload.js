/**
 * Trustwire Overlay Preload Script
 * Provides secure context isolation bridge between native desktop overlay and Electron main process.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('overlayApi', {
  sendAction: (action) => ipcRenderer.send('overlay-action', action),
  dismissAlert: () => ipcRenderer.send('dismiss-overlay-alert'),
  onStateUpdate: (callback) => {
    const handler = (_event, state) => callback(state);
    ipcRenderer.on('state-update', handler);
    return () => ipcRenderer.removeListener('state-update', handler);
  },
  onDisparityAlert: (callback) => {
    const handler = (_event, alert) => callback(alert);
    ipcRenderer.on('disparity-alert', handler);
    return () => ipcRenderer.removeListener('disparity-alert', handler);
  }
});

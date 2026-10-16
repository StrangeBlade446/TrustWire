/**
 * Trustwire Electron Preload Script
 * Provides secure context isolation bridge between native desktop shell and frontend.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('trustwireDesktop', {
  platform: process.platform,
  version: '1.0.0',
  isDesktop: true,
  apiBaseUrl: 'http://127.0.0.1:8765'
});

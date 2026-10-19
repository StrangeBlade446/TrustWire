/**
 * Trustwire Electron Main Process
 * Spawns the local Python FastAPI backend, monitors health, creates the native window,
 * displays an immediate responsive splash screen, and manages the native Windows floating overlay
 * for real-time monitoring controls (play, pause, stop).
 */

const { app, BrowserWindow, dialog, ipcMain, screen, Notification } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow = null;
let overlayWindow = null;
let pythonProcess = null;

const BACKEND_PORT = 8765;
const BACKEND_HOST = '127.0.0.1';
const HEALTH_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}/api/health`;

function getPythonExecutable() {
  if (process.env.PYTHON_PATH && fs.existsSync(process.env.PYTHON_PATH)) {
    return process.env.PYTHON_PATH;
  }
  const py311 = path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python311', 'python.exe');
  if (fs.existsSync(py311)) {
    return py311;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}

const SPLASH_HTML = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Trustwire — Initializing</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      background: #0B0D10;
      color: #E2E8F0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      user-select: none;
    }
    .spinner {
      width: 44px;
      height: 44px;
      border: 3px solid rgba(20, 184, 166, 0.2);
      border-top-color: #2DD4BF;
      border-radius: 50%;
      animation: spin 0.9s cubic-bezier(0.5, 0.1, 0.4, 0.9) infinite;
      margin-bottom: 24px;
    }
    .logo {
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #FFFFFF;
      margin: 0 0 6px 0;
    }
    .tagline {
      font-size: 13px;
      color: #2DD4BF;
      font-weight: 500;
      margin: 0 0 20px 0;
    }
    .status {
      font-size: 12px;
      color: #64748B;
      font-family: monospace;
      margin: 0;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="spinner"></div>
  <div class="logo">TRUSTWIRE</div>
  <div class="tagline">Detect deception before it costs you.</div>
  <p class="status">Loading neural forensics core (ViT • Wav2Vec2 • Whisper)...</p>
</body>
</html>
`;

function waitForBackend(retries = 40, delayMs = 1000) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const check = () => {
      attempts++;
      const req = http.get(HEALTH_URL, (res) => {
        if (res.statusCode === 200) {
          resolve(true);
        } else if (attempts < retries) {
          setTimeout(check, delayMs);
        } else {
          reject(new Error(`Backend responded with status ${res.statusCode}`));
        }
      });

      req.on('error', () => {
        if (attempts < retries) {
          setTimeout(check, delayMs);
        } else {
          reject(new Error(`Could not connect to Trustwire backend at ${HEALTH_URL}`));
        }
      });
      req.end();
    };
    check();
  });
}

function startPythonBackend() {
  const rootDir = path.resolve(__dirname, '..');
  const pythonCmd = getPythonExecutable();
  const args = ['-m', 'uvicorn', 'backend.app:app', '--host', BACKEND_HOST, '--port', String(BACKEND_PORT)];

  console.log(`[Trustwire Desktop] Launching Python backend: ${pythonCmd} ${args.join(' ')}`);

  pythonProcess = spawn(pythonCmd, args, {
    cwd: rootDir,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: '1',
      TRUSTWIRE_API_TOKEN: process.env.TRUSTWIRE_API_TOKEN || 'trustwire_desktop_capability_token'
    },
    stdio: ['ignore', 'pipe', 'pipe']
  });

  pythonProcess.stdout.on('data', (chunk) => {
    const text = chunk.toString().trim();
    if (text) {
      console.log(`[Python Core] ${text}`);
    }
  });

  pythonProcess.stderr.on('data', (chunk) => {
    const text = chunk.toString().trim();
    if (text) {
      console.log(`[Python Core] ${text}`);
    }
  });

  pythonProcess.on('error', (err) => {
    console.error('[Trustwire Desktop] Failed to start Python backend:', err);
    dialog.showErrorBox('Backend Error', `Failed to launch Python engine: ${err.message}`);
  });

  pythonProcess.on('exit', (code, signal) => {
    console.log(`[Trustwire Desktop] Python backend exited with code ${code}, signal ${signal}`);
  });
}

function stopPythonBackend() {
  if (pythonProcess) {
    console.log('[Trustwire Desktop] Terminating Python backend...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
    } else {
      pythonProcess.kill('SIGTERM');
    }
    pythonProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1320,
    height: 880,
    minWidth: 1040,
    minHeight: 720,
    backgroundColor: '#0B0D10',
    title: 'Trustwire — Detect Deception Before It Costs You',
    autoHideMenuBar: true,
    show: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  // Display immediate responsive splash screen while backend initializes
  mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(SPLASH_HTML)}`);

  // Forward renderer console logs to terminal
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[Renderer Console] [Level ${level}] ${message} (${sourceId}:${line})`);
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error(`[Trustwire Desktop] Page load error: ${errorDescription} (${errorCode}) at ${validatedURL}`);
  });

  mainWindow.webContents.on('render-process-gone', (event, details) => {
    console.error('[Trustwire Desktop] Renderer process crashed or killed:', details);
  });

  // Allow developer tools via F12 or Ctrl+Shift+I
  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.key === 'F12' || (input.control && input.shift && input.key.toLowerCase() === 'i')) {
      mainWindow.webContents.toggleDevTools();
      event.preventDefault();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

let lastMonitoringState = null;

function createOverlayWindow() {
  if (overlayWindow && !overlayWindow.isDestroyed()) return;

  const primaryDisplay = screen.getPrimaryDisplay();
  const { width } = primaryDisplay.workAreaSize;
  const overlayWidth = 470;
  const overlayHeight = 56;
  const x = Math.round((width - overlayWidth) / 2);
  const y = 14;

  overlayWindow = new BrowserWindow({
    width: overlayWidth,
    height: overlayHeight,
    x: x,
    y: y,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    movable: true,
    show: false,
    hasShadow: false,
    webPreferences: {
      preload: path.join(__dirname, 'overlay-preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  overlayWindow.setAlwaysOnTop(true, 'screen-saver');
  overlayWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  overlayWindow.loadFile(path.join(__dirname, 'overlay.html'));

  overlayWindow.webContents.on('did-finish-load', () => {
    if (lastMonitoringState && overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.webContents.send('state-update', lastMonitoringState);
    }
  });

  overlayWindow.on('closed', () => {
    overlayWindow = null;
  });
}

// IPC Handlers for Windows Screen Overlay Integration
ipcMain.on('monitoring-state-changed', (event, state) => {
  lastMonitoringState = state;
  // Electron does not pop up a duplicate secondary window over the screen;
  // all monitoring controls and live alerts are managed through the unified UI.
});

ipcMain.on('overlay-action', (event, action) => {
  console.log(`[Trustwire Overlay] Received overlay action: ${action}`);
  if (action === 'focus-main') {
    if (mainWindow && !mainWindow.isDestroyed()) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  } else if (action === 'pause' || action === 'play') {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('remote-monitoring-control', action);
    }
  } else if (action === 'stop') {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('remote-monitoring-control', 'stop');
    }
    // Also perform immediate stop call directly via HTTP to backend
    const req = http.request({
      host: BACKEND_HOST,
      port: BACKEND_PORT,
      path: '/api/monitoring/stop',
      method: 'POST',
      headers: {
        'X-Trustwire-Token': process.env.TRUSTWIRE_API_TOKEN || 'trustwire_desktop_capability_token'
      }
    });
    req.on('error', () => {});
    req.end();

    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.hide();
    }
  }
});

// Disparity Alert Handler for Native Windows Screen Popups
ipcMain.on('disparity-alert', (event, alert) => {
  if (!alert) return;
  // NEVER show desktop screen overlay or notifications for offline media analysis
  if (alert.source !== 'Live Monitoring') return;
  console.log(`[Trustwire Alert] Live Disparity observed: ${alert.category} - ${alert.title}`);

  // 1. Show Native Windows OS Toast Notification
  try {
    if (Notification && Notification.isSupported()) {
      const disparityLabel = 
        alert.category === 'video_deepfake' ? 'Visual Disparity (Face Tampering / Generation)' :
        'Acoustic Disparity (Synthetic Voice / Clone)';

      new Notification({
        title: `🚨 ${disparityLabel}`,
        body: `${alert.title}\nAction: ${alert.suggested_action}`,
        silent: false
      }).show();
    }
  } catch (e) {
    console.error('[Trustwire Desktop] Notification toast error:', e);
  }
});

app.whenReady().then(async () => {
  // 1. Create window immediately with splash animation
  createWindow();

  // 2. Start Python forensic core
  startPythonBackend();

  try {
    console.log('[Trustwire Desktop] Waiting for Python forensic core to initialize...');
    await waitForBackend(45, 1000);
    console.log('[Trustwire Desktop] Python backend verified active.');

    // 3. Smoothly transition to the main React distribution
    const indexPath = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
    console.log(`[Trustwire Desktop] Loading frontend dashboard: ${indexPath}`);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.loadFile(indexPath).catch((err) => {
        console.error('[Trustwire Desktop] Failed to load frontend HTML:', err);
      });
    }
  } catch (err) {
    console.error('[Trustwire Desktop] Backend initialization timed out:', err);
    if (mainWindow && !mainWindow.isDestroyed()) {
      const errorHtml = `
        <body style="background:#0B0D10;color:#F43F5E;font-family:sans-serif;padding:40px;text-align:center;">
          <h2>Backend Initialization Timeout</h2>
          <p style="color:#94A3B8;font-size:13px;">${err.message}</p>
          <p style="color:#64748B;font-size:12px;">Ensure port 8765 is free and Python dependencies are installed.</p>
        </body>
      `;
      mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(errorHtml)}`);
    }
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopPythonBackend();
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.close();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopPythonBackend();
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.close();
  }
});

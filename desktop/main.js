/**
 * Trustwire Electron Main Process
 * Spawns the local Python FastAPI backend, monitors health, creates the native window,
 * and handles graceful application shutdown and cleanup.
 */

const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow = null;
let pythonProcess = null;

const BACKEND_PORT = 8765;
const BACKEND_HOST = '127.0.0.1';
const HEALTH_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}/api/health`;

function waitForBackend(retries = 30, delayMs = 1000) {
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
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  const args = ['-m', 'uvicorn', 'backend.app:app', '--host', BACKEND_HOST, '--port', String(BACKEND_PORT)];

  console.log(`[Trustwire Desktop] Launching Python backend: ${pythonCmd} ${args.join(' ')}`);

  pythonProcess = spawn(pythonCmd, args, {
    cwd: rootDir,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: '1',
      TRUSTWIRE_API_TOKEN: process.env.TRUSTWIRE_API_TOKEN || 'trustwire_desktop_capability_token'
    },
    stdio: 'inherit'
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
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  // Load production built React distribution
  const indexPath = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
  mainWindow.loadFile(indexPath).catch((err) => {
    console.error('Failed to load frontend HTML:', err);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  startPythonBackend();

  try {
    console.log('[Trustwire Desktop] Waiting for Python forensic core to initialize...');
    await waitForBackend(45, 1000);
    console.log('[Trustwire Desktop] Python backend verified active.');
    createWindow();
  } catch (err) {
    console.error('[Trustwire Desktop] Backend initialization timed out:', err);
    dialog.showErrorBox(
      'Startup Warning',
      'Trustwire Python backend could not be verified within 45 seconds. Check if port 8765 is occupied.'
    );
    createWindow();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopPythonBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopPythonBackend();
});

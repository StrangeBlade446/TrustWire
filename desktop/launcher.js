/**
 * Trustwire Universal Desktop Launcher
 * Launches the native Electron application with the Python backend.
 */

const { spawn } = require('child_process');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const electronBin = process.platform === 'win32'
  ? path.join(rootDir, 'node_modules', 'electron', 'dist', 'electron.exe')
  : 'electron';

const mainScript = path.join(__dirname, 'main.js');

console.log('====================================================');
console.log(' TRUSTWIRE — Detect deception before it costs you.');
console.log(' Windows Desktop Application Launcher');
console.log('====================================================');
console.log(`Starting Electron shell: ${electronBin}`);

const child = spawn(electronBin, [mainScript], {
  cwd: rootDir,
  stdio: 'inherit'
});

child.on('exit', (code) => {
  console.log(`Trustwire exited with status code: ${code}`);
  process.exit(code || 0);
});

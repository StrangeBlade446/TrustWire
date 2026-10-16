@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   TRUSTWIRE — Detect deception before it costs you.
echo   Windows Application Launcher
echo ========================================================

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.11+ is not found in PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not found in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/3] Verifying Python backend dependencies...
python -c "import fastapi, uvicorn, onnxruntime, torch, faster_whisper, soundcard, mss; print('All core Python dependencies verified.')"
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies missing. Installing requirements.txt...
    python -m pip install -r requirements.txt
)

echo [2/3] Checking frontend build...
if not exist "frontend\dist\index.html" (
    echo [INFO] Building frontend bundle...
    cd frontend && npm run build && cd ..
)

echo [3/3] Launching Trustwire Desktop Application...
npm start

endlocal

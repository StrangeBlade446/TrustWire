# Trustwire Windows PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  TRUSTWIRE — Detect deception before it costs you." -ForegroundColor White
Write-Host "  Windows 10/11 Desktop Launcher" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not found in PATH. Please install Python 3.11+."
    exit 1
}
Write-Host "[1/3] Python verified: $pythonVersion" -ForegroundColor Green

# 2. Check Node
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Node.js is not found in PATH. Please install Node.js v20+."
    exit 1
}
Write-Host "[2/3] Node.js verified: $nodeVersion" -ForegroundColor Green

# 3. Check frontend distribution
if (-not (Test-Path "frontend\dist\index.html")) {
    Write-Host "Building frontend assets..." -ForegroundColor Yellow
    Push-Location frontend
    npm run build
    Pop-Location
}

# 4. Launch Desktop Shell
Write-Host "[3/3] Starting Trustwire Electron + FastAPI Core..." -ForegroundColor Cyan
npm start

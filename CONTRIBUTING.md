# Contributing to Trustwire

Thank you for your interest in contributing to Trustwire! We welcome contributions that improve reliability, detection precision, privacy enforcement, and Windows platform integration.

## Code of Conduct

Please maintain a collaborative, respectful, and constructive environment.

## Development Setup

1. **Prerequisites:**
   - Windows 10 or 11 x64 (Windows 11 recommended)
   - Python 3.11+
   - Node.js v20+ and npm
   - FFmpeg 6.0+ (accessible in PATH)

2. **Clone and Install:**
   ```powershell
   git clone https://github.com/your-username/trustwire.git
   cd trustwire

   # Install Python dependencies
   pip install -r requirements.txt

   # Install Node and frontend dependencies
   npm install
   cd frontend
   npm install
   cd ..
   ```

3. **Running the Development Environment:**
   ```powershell
   # Start the backend and electron desktop shell
   npm start
   ```

4. **Running Automated Tests:**
   ```powershell
   # Run all Python unit, detector smoke, and integration tests
   python -m pytest

   # Run frontend build verification
   cd frontend
   npm run build
   ```

## Development Guidelines

- **Zero Mock Policy in Production:** Never submit synthetic random confidence scores, fabricated detection probabilities, or mock models in production pathways. If a model is unavailable, report `Unavailable` or `Inconclusive` honestly.
- **Privacy First:** Ensure all captured buffers respect the 15-minute maximum retention policy. Never write raw media to alert history or logs.
- **Test Coverage:** Accompany all rule adjustments or model additions with unit and regression tests in `tests/`.

## Pull Request Process

1. Fork the repository and create your feature branch from `main`.
2. Ensure all pytest tests pass and frontend build succeeds without TypeScript errors.
3. Update `BUILD_STATUS.md` and `CHANGELOG.md` with relevant details.
4. Submit a descriptive Pull Request outlining the changes and verification evidence.

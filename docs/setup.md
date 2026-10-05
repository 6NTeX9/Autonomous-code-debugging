# Installation & Setup Guide

This guide covers local environment setup, Docker Compose deployment, and running automated tests.

---

## Prerequisites
- **Python**: 3.10+ (Python 3.11 / 3.12 / 3.13 tested)
- **Node.js**: v18+ (Node v20 / v23 tested)
- **Git**: Installed and available in PATH
- **Docker** (optional): For containerized execution

---

## 1. Quick Start (Local Development)

### Step 1: Clone or Navigate to the Workspace
```bash
cd "autonomous-code-debugger"
```

### Step 2: Set Up Backend
```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### Step 3: Set Up Frontend
```bash
cd ../frontend
npm install
npm run build
```

### Step 4: Set Up Sample Buggy Project
```bash
cd ../sample-project
npm install
npm test # Runs baseline: exactly 18 passed, 3 failed
```

---

## 2. Running the Application

### Option A: Launch Backend and Frontend Separately
- **Terminal 1 (Backend API):**
  ```bash
  ./scripts/run_backend.sh
  ```
  Backend starts on `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

- **Terminal 2 (Frontend Dashboard):**
  ```bash
  ./scripts/run_frontend.sh
  ```
  Dashboard opens on `http://localhost:3000`.

### Option B: Run Standalone CLI Demonstration
```bash
./scripts/run_demo.sh
```

---

## 3. Running with Docker Compose

```bash
docker-compose up --build
```
- Access dashboard at `http://localhost:3000`
- Access API at `http://localhost:8000`

---

## 4. Running Backend Automated Tests

```bash
cd backend
./venv/bin/pytest tests/ -v
```
All 13 unit, integration, agent, tool, and E2E pipeline tests will execute and pass.

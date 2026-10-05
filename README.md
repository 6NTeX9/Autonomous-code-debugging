# AUTONOMOUS CODE DEBUGGING AGENT
### Agentic AI Mini Project — ILP CCA 2 (Group of 4 Students)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg?logo=next.js)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/Sample-TypeScript%20%2F%20Jest-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![Pytest](https://img.shields.io/badge/Tests-13%20Passed-brightgreen.svg?logo=pytest)](https://pytest.org)

An autonomous multi-agent self-healing software engineering system. Unlike passive chatbots that merely explain stack traces, this system actively **inspects repositories**, **executes test suites in sandboxes**, **reasons over root causes**, **synthesizes minimal safe patches**, **manages Git checkpoints**, **validates outcomes against regressions**, and **iteratively self-heals defects until 100% test pass rates are verified**.

---

## 1. Project Overview & Motivation

Modern software systems spend over 50% of developer hours diagnosing regressions, debugging edge-case logic, and validating patches. While generative AI models can generate code snippets, single-turn LLM prompts frequently introduce regressions, hallucinate APIs, or break unrelated modules.

The **Autonomous Code Debugging Agent** implements an **Agentic AI architecture** with four specialized roles that collaborate through structured data contracts, maintain Git checkpoints, and execute a closed feedback loop:

```
USER / OPERATOR
      ↓
CENTRAL ORCHESTRATOR
      ↓
[AGENT 1: SCOUT]      → Inspects codebase, runs tests, isolates failing modules
      ↓
[AGENT 2: DETECTIVE]  → Analyzes call sites, formulates hypotheses, determines root cause
      ↓
[AGENT 3: REPAIRER]   → Enforces safety rules, creates Git checkpoint, applies patch
      ↓
[AGENT 4: GUARDIAN]   → Re-executes tests in sandbox, checks regressions
      ↓
TEST OUTCOME
  ├── 100% PASS → FINAL AUTONOMOUS REPORT (VERIFIED)
  └── FAILURES  → DETECTIVE → REPAIRER → GUARDIAN (Retries up to MAX_ITERATIONS = 5)
```

---

## 2. Four-Agent Architecture & Team Ownership

The system architecture contains **exactly four primary specialized AI agents**:

| Agent | Role | Team Ownership | Core Responsibilities & Tools |
| :--- | :--- | :--- | :--- |
| **Agent 1: SCOUT** | Repository & Error Analysis | **Member 1** | Traverses repository structure (`list_files`), detects language & framework (`detect_project_type`), analyzes dependencies (`analyze_dependencies`), runs baseline tests (`run_tests`), captures stack traces (`inspect_error_log`), and emits structured `ScoutOutput`. |
| **Agent 2: DETECTIVE** | Root Cause & Reasoning | **Member 2** | Reads source code (`read_file`), traces callers and callees (`search_code`), formulates competing hypotheses with confidence ratings (0.0 to 1.0), isolates empirical evidence, selects the verified root cause, and prescribes repair strategies. **Never exposes hidden chain-of-thought**. |
| **Agent 3: REPAIRER** | Fix Generation & Code Repair | **Member 3** | Strictly adheres to safety rules (never delete tests, never weaken assertions, minimal safe patch). Establishes a Git checkpoint (`create_git_checkpoint`), applies modifications (`apply_patch`), and generates diffs (`get_git_diff`). |
| **Agent 4: GUARDIAN** | Validation & Testing | **Member 4** | Executes test suites inside the isolated sandbox (`run_tests`), compares before/after metrics, checks for regressions, approves valid patches, and triggers immediate rollback (`rollback_changes`) if regressions occur. |

---

## 3. Technology Stack

- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic v2.
- **Real-Time Streaming:** WebSocket (`/ws/debug/{session_id}`) & Server-Sent Events.
- **Database:** SQLite (persisting Projects, Sessions, Events, Hypotheses, Patches, TestRuns, Reports).
- **Execution Sandboxing:** Dual-mode Sandbox (Docker containerized jail or secure isolated Process driver with path-traversal guards, timeouts, and sanitized environments).
- **Version Control:** Git (checkpoints, unified diff calculation, and hard rollbacks).
- **LLM Abstraction:** Pluggable `LLMProvider` with `OpenAIProvider` (GPT-4o or any compatible API) and an intelligent deterministic `MockProvider` for 100% offline demonstration without API keys.

---

## 4. Built-in Sample Buggy Project (`sample-project`)

The project includes an intentional realistic E-commerce & Order Management microservice:
- **Stack:** TypeScript, Express, Jest test suite.
- **Total Tests:** Exactly **21 tests**.
- **Initial Baseline State:** **18 PASSED, 3 FAILED**.

### The 3 Intentional Realistic Defects:
1. **Bug 1 (Null/Undefined Handling):** `userController.ts` accesses `user.name` without checking for missing records when `getUserById` returns undefined, throwing `TypeError: Cannot read properties of undefined (reading 'name')`.
2. **Bug 2 (Incorrect Business Logic):** `discountService.ts` applies a 15% discount instead of 20% for VIP orders and uses strict `> 100` instead of `>= 100`.
3. **Bug 3 (Edge-Case Calculation):** `orderService.ts` shipping fee calculation fails to grant free shipping on orders meeting the `$50` threshold or using coupon code `FREE_SHIP`.

---

## 5. Quick Start & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.13)
- Node.js v18+ (tested on v20, v23)
- Git

### 1. Clone & Set Up Python Backend
```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 2. Set Up Next.js Frontend
```bash
cd ../frontend
npm install
npm run build
```

### 3. Set Up Sample Project
```bash
cd ../sample-project
npm install
npm test # Verifies initial state: 18 passed, 3 failed
```

---

## 6. Running the System

### Option A: Launch Interactive Dashboard (Recommended)
- **Terminal 1 (Backend API):**
  ```bash
  ./scripts/run_backend.sh
  ```
  API runs on `http://localhost:8000` (Interactive Swagger docs: `http://localhost:8000/docs`).

- **Terminal 2 (Frontend Dashboard):**
  ```bash
  ./scripts/run_frontend.sh
  ```
  Open `http://localhost:3000` in your web browser.

### Option B: Standalone CLI Demonstration
```bash
./scripts/run_demo.sh
```

### Option C: Docker Compose
```bash
docker-compose up --build
```

---

## 7. Running Automated Test Suite

The system includes comprehensive automated tests covering all layers:
```bash
cd backend
./venv/bin/pytest tests/ -v
```
**Test Results (13/13 Passed):**
- `test_sandbox_safe_execution`: Sandboxed command runner and output capture.
- `test_sandbox_timeout`: Enforced timeout and process termination.
- `test_sandbox_path_traversal_protection`: Path escape and directory traversal prevention.
- `test_sandbox_env_sanitization`: Credential stripping from execution environments.
- `test_filesystem_tools`: File search, line reading, metadata extraction.
- `test_git_checkpoint_and_rollback`: Git snapshotting and hard rollback restoration.
- `test_jest_output_parser`: Regex and JSON test result parsing.
- `test_detective_agent`: Hypothesis formulation and root cause isolation.
- `test_guardian_regression_detection`: Regression gating and patch rejection.
- `test_health`: FastAPI service health check.
- `test_load_sample_project`: Sample project workspace initialization.
- `test_get_project_not_found`: 404 error handling.
- `test_full_autonomous_debugging_pipeline`: Complete end-to-end multi-agent self-healing loop.

---

## 8. Classroom Demonstration Walkthrough

Follow these steps when demonstrating to professors or evaluators:
1. Open `http://localhost:3000`.
2. Click **"Load Demo Project"** in the navigation header.
3. Observe the initial state: **21 tests total (18 passed, 3 failed)**.
4. Click **"Start Autonomous Debug"** (Mode: AUTO).
5. Watch the animated **Agent Pipeline** cycle through:
   - **SCOUT** analyzes repository, detects TypeScript/Express/Jest, and isolates failing test cases.
   - **DETECTIVE** examines call sites, ranks competing hypotheses with confidence percentages (e.g. 95%), and isolates empirical code evidence without revealing hidden chain-of-thought.
   - **REPAIRER** creates a Git checkpoint and generates a minimal safe patch (visible in the unified diff viewer).
   - **GUARDIAN** validates test execution, measures progress (18 → 19 → 20 → 21 passing), and detects zero regressions.
6. The system autonomously loops across 3 iterations and displays:
   - **21 PASSED, 0 FAILED**
   - **PATCH VERIFIED**
   - **DEBUGGING SUCCESSFUL**
7. Click **"View Final Report"** to inspect or copy the verified outcome report.

---

## 9. Academic Requirements Mapping (ILP CCA 2)

| Requirement | Description | System Implementation |
| :--- | :--- | :--- |
| **Requirement 1** | Understands the problem | **Agent 1 (Scout):** Traverses repo, detects runtime, executes baseline tests, extracts stack traces. |
| **Requirement 2** | Reasons and makes decisions | **Agent 2 (Detective):** Generates ranked hypotheses, evaluates evidence, isolates root cause. |
| **Requirement 3** | Uses appropriate tools | **All Agents:** 14 deterministic tools (`read_file`, `search_code`, `git_checkpoint`, `run_tests`, etc.). |
| **Requirement 4** | Performs tasks autonomously | **Agent 3 (Repairer) & Orchestrator:** Checkpoint management, safe diff patching, closed retry loop. |
| **Requirement 5** | Generates desired outcome | **Agent 4 (Guardian):** Re-runs tests, verifies 0 regressions, generates verified outcome report. |

Detailed mapping documentation is available in [`docs/cca-requirements-mapping.md`](docs/cca-requirements-mapping.md).

---

## 10. Documentation Index

- [`docs/architecture.md`](docs/architecture.md): Complete architecture diagram and technical specifications.
- [`docs/agent-design.md`](docs/agent-design.md): In-depth agent profiles, system prompts, and tool access matrices.
- [`docs/agent-communication.md`](docs/agent-communication.md): JSON schema data contracts between agents.
- [`docs/api.md`](docs/api.md): REST and WebSocket API specification.
- [`docs/setup.md`](docs/setup.md): Complete installation and environment setup instructions.
- [`docs/demo.md`](docs/demo.md): Exact step-by-step classroom demonstration script.
- [`docs/security.md`](docs/security.md): Sandbox protections, path traversal guards, and timeout limits.
- [`docs/limitations.md`](docs/limitations.md): Current architectural scope and roadmap.
- [`docs/cca-requirements-mapping.md`](docs/cca-requirements-mapping.md): Academic syllabus requirements mapping.

---

## 11. License

MIT License. Designed and built for the **ILP CCA 2 Agentic AI Mini-Project**.

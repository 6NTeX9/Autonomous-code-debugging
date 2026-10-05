# Classroom Demonstration Guide (Demo Mode)

**Audience:** Professors, evaluators, and students  
**Goal:** Demonstrate that the Autonomous Code Debugging Agent is NOT a simple chatbot, but a genuine self-healing agentic system that understands code, reasons about root causes, executes tools, establishes checkpoints, applies patches, validates against test suites, recovers from failures, and produces a verified outcome.

---

## Classroom Demonstration Walkthrough (Step-by-Step)

### Step 1: Open the Dashboard
1. Ensure the backend is running (`./scripts/run_backend.sh`) and frontend is running (`./scripts/run_frontend.sh`).
2. Open your web browser to `http://localhost:3000`.
3. Highlight the dark developer dashboard with the 4-agent pipeline header:
   `SCOUT` → `DETECTIVE` → `REPAIRER` → `GUARDIAN`.

### Step 2: Load the Buggy Sample Project
1. Click **"Load Demo Project"** in the top navigation bar.
2. Point out the baseline project details:
   - **Project Name:** `sample-buggy-project`
   - **Stack:** TypeScript, Express microservice, Jest test suite.
   - **Baseline Test Suite:** **21 tests total: 18 PASSED, 3 FAILED**.
3. Point out the 3 intentional realistic defects in the Error Panel:
   - **Bug 1:** Null/undefined handling in `userController.ts` (`TypeError: Cannot read properties of undefined (reading 'name')`).
   - **Bug 2:** Incorrect business logic in `discountService.ts` (VIP tier discount rate and `>= 100` boundary condition).
   - **Bug 3:** Edge-case calculation in `orderService.ts` (Free shipping threshold on orders `>= $50` or coupon `FREE_SHIP`).

### Step 3: Trigger Autonomous Self-Healing
1. Ensure the mode is set to **"Autonomous (AUTO)"**.
2. Click **"Start Autonomous Debug"**.

### Step 4: Observe Agent 1 — SCOUT in Action
1. Watch the pipeline highlight **Agent 1: SCOUT** with a live pulsing glow.
2. In the **Agent Activity Console**, point out:
   - `list_files()`: Cataloging directory structure.
   - `detect_project_type()`: Detecting TypeScript / Express / Jest.
   - `run_tests()`: Executing baseline tests inside the isolated sandbox.
   - `inspect_error_log()`: Parsing stack frames and isolating `src/controllers/userController.ts`.

### Step 5: Observe Agent 2 — DETECTIVE Reasoning
1. Pipeline transitions to **Agent 2: DETECTIVE**.
2. Point out the **Reasoning Summary Panel**:
   - Multiple competing hypotheses with confidence percentages (e.g. 95% vs 35% vs 20%).
   - Empirical evidence extracted from code inspection.
   - **Zero Hidden Chain-of-Thought:** Clean, evidence-based reasoning suitable for executive review.

### Step 6: Observe Agent 3 — REPAIRER & Safety Rules
1. Pipeline transitions to **Agent 3: REPAIRER**.
2. In the **Code Patch & Diff Viewer**, point out:
   - Git Checkpoint created (`checkpoint_before_iteration_1`).
   - Unified Git Diff: Green addition of defensive `if (!user) return res.status(404)`.
   - Strict Safety Rule verification: Zero test files were modified or deleted.

### Step 7: Observe Agent 4 — GUARDIAN Validation
1. Pipeline transitions to **Agent 4: GUARDIAN**.
2. Tests are re-executed in the sandbox:
   - Tests Before: 18 passed / 3 failed
   - Tests After: 19 passed / 2 failed
   - Regressions: 0.
3. Guardian issues `PARTIALLY_VERIFIED`.
4. Orchestrator automatically re-routes remaining failures back to Detective for Iteration 2!

### Step 8: Multi-Iteration Progression & Final Verification
1. Watch Iteration 2 resolve the discount service defect (20 passed / 1 failed).
2. Watch Iteration 3 resolve the shipping calculation defect:
   - **21 PASSED, 0 FAILED**!
3. Guardian issues **PATCH VERIFIED**!
4. The system automatically displays the **Autonomous Debugging Report Modal**:
   - Status: **SUCCESS**
   - Validation Result: **VERIFIED**
   - Tests Before: 18 passed / 3 failed
   - Tests After: **21 passed / 0 failed**
   - Regressions: **0**
   - Iterations: **3**
   - Confidence: **High**

---

## Human-in-the-Loop Demonstration (Optional Variant)
1. Switch mode to **"Approval Required"** in the navigation header.
2. Click **"Start Autonomous Debug"**.
3. When Detective completes reasoning, the workflow pauses and presents the **Human Intervention Modal**.
4. Show the professor the proposed patch and confidence score, then click **"Approve & Apply Patch"** to proceed.

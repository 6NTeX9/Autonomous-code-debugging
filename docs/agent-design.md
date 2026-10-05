# Agent Design & Responsibilities Specification

## 1. AGENT 1 — SCOUT (Repository & Error Analysis Agent)
- **Role:** Observes and isolates the environment without speculation.
- **Responsibilities:**
  - Traverses the directory tree to catalog project assets.
  - Detects language (TypeScript, JavaScript, Python, Java) and frameworks (Express, NestJS, FastAPI, etc.).
  - Inspects package manifests (`package.json`, `requirements.txt`).
  - Executes initial baseline test suite.
  - Captures stdout/stderr, extracts stack traces, and isolates failing test titles.
  - Identifies affected source files and candidate symbols/functions.
- **Output:** Structured `ScoutOutput` contract.

---

## 2. AGENT 2 — DETECTIVE (Root Cause & Reasoning Agent)
- **Role:** Evaluates failure evidence, traces call sites, and deduces root causes.
- **Responsibilities:**
  - Reads relevant source code files discovered by Scout.
  - Traces callers and callees across methods.
  - Generates multiple competing hypotheses with confidence ratings (0.0 to 1.0).
  - Gathers empirical code evidence supporting or refuting each hypothesis.
  - Determines the highest-confidence root cause.
  - Prescribes repair strategies and architectural constraints.
  - **No Hidden CoT:** Only surfaces concise, evidence-based reasoning summaries.
- **Output:** Structured `DetectiveOutput` contract.

---

## 3. AGENT 3 — REPAIRER (Fix Generation & Code Repair Agent)
- **Role:** Crafts and applies minimal safe code modifications.
- **Strict Safety Rules:**
  1. NEVER delete test files or test assertions to make tests pass.
  2. NEVER weaken assertions or expected values.
  3. NEVER disable validation logic or comment out broken code.
  4. Preserve public API contracts and existing coding styles.
  5. Always create a Git checkpoint before modifying files.
- **Responsibilities:**
  - Establishes git checkpoint (`create_git_checkpoint`).
  - Formulates minimal safe patch addressing the root cause.
  - Applies patch cleanly to workspace files.
  - Generates unified git diff for human review.
- **Output:** Structured `RepairerOutput` contract.

---

## 4. AGENT 4 — GUARDIAN (Validation & Testing Agent)
- **Role:** Empirical validator and regression gatekeeper.
- **Responsibilities:**
  - Re-executes the test suite in the sandbox after the patch is applied.
  - Compares test suite metrics before and after repair.
  - Checks for regressions (if previously passing tests now fail).
  - If regressions occur: triggers immediate rollback to the git checkpoint and sends results back to Detective.
  - If progress is made: approves partial patch and reinvestigates remaining failures.
  - If all tests pass: issues `PATCH_VERIFIED` decision and concludes session.
- **Output:** Structured `GuardianOutput` contract.

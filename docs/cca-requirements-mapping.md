# Academic Requirements Mapping (ILP CCA 2)

**Project Title:** AUTONOMOUS CODE DEBUGGING AGENT  
**Group:** 4 Students  
**Course / Evaluation:** ILP Continuous Course Assessment 2 (CCA 2)

This document explicitly maps the five core Agentic AI requirements of the ILP CCA 2 project to the implemented four-agent software architecture.

---

## Academic Requirement 1: Understands the Problem
> *The AI system must be capable of observing the environment, inspecting repository structure, and understanding the nature of software failures.*

### Architectural Implementation:
- **Agent 1 (SCOUT — Repository & Error Analysis Agent):**
  - **Owned by:** Member 1.
  - **Actions:** Inspects repository tree (`list_files`), detects language and runtime frameworks (`detect_project_type`), analyzes package manifests (`analyze_dependencies`), runs initial baseline test suites (`run_tests`), captures raw stdout/stderr, and isolates failing test assertions and stack traces (`inspect_error_log`).
  - **Outcome:** Emits a structured `ScoutOutput` contract isolating affected source files (`userController.ts`, `discountService.ts`, `orderService.ts`) and failing assertion messages.

---

## Academic Requirement 2: Reasons and Makes Decisions
> *The AI system must not merely echo errors, but logically analyze call sites, formulate competing hypotheses, rank evidence, and deduce the root cause.*

### Architectural Implementation:
- **Agent 2 (DETECTIVE — Root Cause & Reasoning Agent):**
  - **Owned by:** Member 2.
  - **Actions:** Reads relevant source code (`read_file`), traces callers and callees (`search_code`), and compares intended specifications with actual code implementations.
  - **Hypothesis Ranking:** Generates multiple competing hypotheses (e.g. database unhandled undefined vs route parsing failure vs mock database failure) with quantitative confidence scores (0.0 to 1.0) and concrete evidence lists.
  - **Decision:** Determines the single highest-confidence root cause, formulates an architectural repair strategy, and defines constraints (e.g. preserve public APIs, never weaken tests).
  - **No Hidden CoT:** Surfaces concise, evidence-backed reasoning summaries to the dashboard without leaking internal chain-of-thought tokens.

---

## Academic Requirement 3: Uses Appropriate Tools
> *The AI system must integrate specialized, deterministic tools to interact with codebases and environments rather than hallucinating answers.*

### Architectural Implementation:
- **Dedicated Tool Suite:** All four agents interact with the repository strictly through structured tools:
  1. `list_files(path)`: Recursive directory walker.
  2. `read_file(path)`: Line-ranged safe file reader.
  3. `search_code(query)`: Workspace regex and keyword matcher.
  4. `get_file_metadata(path)`: File statistics and line counters.
  5. `detect_project_type()`: Automatic framework and language detection.
  6. `analyze_dependencies()`: Manifest dependency inspection.
  7. `run_command(cmd)`: Isolated sandboxed execution.
  8. `run_tests()`: Test runner discovery and execution (Jest, Pytest).
  9. `get_test_results()`: Structured assertion output parsing.
  10. `inspect_error_log()`: Stack trace and frame parser.
  11. `create_git_checkpoint()`: Git commit and tag state checkpoints.
  12. `apply_patch(patch)`: Safe unified diff and file patching.
  13. `get_git_diff()`: Exact repository diff calculation.
  14. `rollback_changes()`: Hard reset to restore clean checkpoint state.
- **Event System:** Every single tool call and tool result emits an observable `AgentEvent` stored in SQLite and streamed to the UI via WebSockets.

---

## Academic Requirement 4: Performs Tasks Autonomously
> *The system must autonomously synthesize repairs, manage rollback checkpoints, and execute closed feedback loops without requiring step-by-step human prompts.*

### Architectural Implementation:
- **Agent 3 (REPAIRER — Fix Generation & Code Repair Agent):**
  - **Owned by:** Member 3.
  - **Actions:** Enforces strict safety rules (never delete tests, never weaken assertions). Generates minimal safe patches, establishes a git checkpoint (`create_git_checkpoint`), applies modifications (`apply_patch`), and generates diffs (`get_git_diff`).
- **Central Orchestrator Feedback Loop:**
  - Manages multi-iteration self-healing (up to `MAX_ITERATIONS = 5`).
  - If a patch fails validation or introduces regressions, the orchestrator triggers immediate rollback and loops back to Agent 2 (Detective) with the new failure information.
  - Human-in-the-Loop options: Supports both pure autonomous (`AUTO`) and supervised (`APPROVAL_REQUIRED`) modes.

---

## Academic Requirement 5: Generates Desired Outcome
> *The system must validate its modifications against the environment and verify that all failing tests pass with zero regressions.*

### Architectural Implementation:
- **Agent 4 (GUARDIAN — Validation & Testing Agent):**
  - **Owned by:** Member 4.
  - **Actions:** Re-runs the test suite in the secure sandbox, compares test metrics before and after the patch, and inspects for regressions.
  - **Decision Logic:** Emits `PATCH_VERIFIED` only when 100% of tests pass and regressions equal zero. If regressions occur, immediately calls `rollback_changes()`.
- **Autonomous Debugging Report:**
  - Generates the final academic summary (`DebugReport`):
    - Tests Before: 18 passed / 3 failed
    - Tests After: 21 passed / 0 failed
    - Regressions: 0
    - Status: SUCCESS (Verified)

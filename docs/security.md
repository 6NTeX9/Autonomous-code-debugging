# Sandbox & Security Architecture

Untrusted code execution is one of the highest-risk operations in autonomous agentic software. This system enforces a defense-in-depth security model to protect host infrastructure against malicious repositories and destructive actions.

---

## 1. Threats Mitigated

| Threat Vector | Mitigation Mechanism |
| :--- | :--- |
| **Path Traversal / Directory Escape** | `validate_safe_path()` strictly verifies that every accessed or written path resolves inside the target workspace. Any `..` or absolute escape raises `SecurityViolationError`. |
| **Zip Slip & Malicious Archives** | `safe_extract_zip()` validates archive header paths before extracting, refusing entries with `..`, absolute paths, or invalid symlinks. |
| **Zip Bombs / Resource Exhaustion** | Strict uncompressed size ceiling (maximum 50 MB total archive bytes allowed). |
| **Infinite Loops & Test Timeouts** | Enforced asynchronous subprocess / container execution timeout (`EXECUTION_TIMEOUT_SECONDS = 60s`). Processes exceeding limits are forcibly killed via `SIGKILL`. |
| **Secret / Credential Leaks** | Subprocess environment sanitizer strips sensitive variables (`LLM_API_KEY`, `OPENAI_API_KEY`, `AWS_ACCESS_KEY_ID`, `DATABASE_URL`, `SECRET_KEY`). |
| **Destructive File Rewrites** | Mandatory Git checkpoint (`create_git_checkpoint`) created before every patch application. If regressions occur, `rollback_changes` executes `git reset --hard` and `git clean -fd`. |
| **Container Jail (Docker Mode)** | Containers run with `--memory=512m`, `--cpus=1.5`, `--pids-limit=100`, unprivileged user (`1000:1000`), and restricted network. |

---

## 2. Dual-Mode Resilient Sandbox Architecture

The system implements a pluggable `SandboxDriver` interface:
1. `DockerSandboxDriver`: Provisions containerized workspaces for full kernel-level isolation.
2. `ProcessSandboxDriver`: Provides secure process isolation with resource limits and path security checks, ensuring zero-dependency portability across CI/CD and developer laptops.
3. `get_sandbox_driver()`: Auto-provisions the best available secure driver based on host daemon availability.

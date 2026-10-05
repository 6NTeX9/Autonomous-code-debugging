# Agent Communication & Structured Contracts

The Autonomous Code Debugging Agent architecture strictly forbids uncontrolled free-form text strings between agents. All inter-agent data exchanges occur through strongly-typed Pydantic schemas.

---

## 1. Scout → Detective (`ScoutOutput`)

```json
{
  "session_id": "debug_001",
  "project": "sample-ecommerce-service",
  "language": "TypeScript",
  "framework": "Express",
  "test_framework": "Jest",
  "source_dirs": ["src"],
  "test_dirs": ["tests"],
  "entry_points": ["src/index.ts"],
  "dependencies": ["express", "typescript", "jest"],
  "initial_test_summary": {
    "total": 21,
    "passed": 18,
    "failed": 3
  },
  "failures": [
    {
      "test": "should return 404 for missing user",
      "error": "TypeError: Cannot read properties of undefined (reading 'name')",
      "file": "src/controllers/userController.ts",
      "line": 21
    }
  ],
  "stack_trace": "...",
  "affected_files": ["src/controllers/userController.ts"],
  "relevant_symbols": ["getUser()"]
}
```

---

## 2. Detective → Repairer (`DetectiveOutput`)

```json
{
  "session_id": "debug_001",
  "iteration": 1,
  "hypotheses": [
    {
      "description": "Database query returns undefined for non-existent user ID, but userController accesses user.name directly without null guard.",
      "evidence": [
        "userRepository.getUserById returns undefined when id does not exist",
        "userController.ts line 21 accesses user.name directly"
      ],
      "affected_files": ["src/controllers/userController.ts"],
      "confidence": 0.95
    }
  ],
  "root_cause": "Missing-user case is not handled in userController.ts. When a user ID is not found, userRepository.getUserById() returns undefined.",
  "evidence": [
    "userController.ts line 21 accesses user.name without null check",
    "Tests expect HTTP 404 with { error: 'User not found' }"
  ],
  "affected_files": ["src/controllers/userController.ts"],
  "confidence": 0.95,
  "repair_strategy": "Add defensive check for !user returning 404 before accessing properties.",
  "constraints": [
    "Preserve existing API response contract",
    "Do not alter user repository interface"
  ],
  "reasoning_summary": "Tests indicate that getUser() can return undefined. Inspected call sites in userController.ts. The controller assumes a user always exists. Confidence: 95%."
}
```

---

## 3. Repairer → Guardian (`RepairerOutput`)

```json
{
  "session_id": "debug_001",
  "iteration": 1,
  "patch_id": "patch_user_controller_null_check_01",
  "modified_files": ["src/controllers/userController.ts"],
  "diff": "--- a/src/controllers/userController.ts\n+++ b/src/controllers/userController.ts\n@@ -19,4 +19,8 @@\n+    if (!user) {\n+      res.status(404).json({ error: 'User not found' });\n+      return;\n+    }",
  "checkpoint": "checkpoint_before_iteration_1",
  "patch_summary": "Added defensive missing-user check returning 404 'User not found'."
}
```

---

## 4. Guardian → Orchestrator / Detective (`GuardianOutput`)

```json
{
  "session_id": "debug_001",
  "iteration": 1,
  "tests_before": {
    "total": 21,
    "passed": 18,
    "failed": 3
  },
  "tests_after": {
    "total": 21,
    "passed": 19,
    "failed": 2
  },
  "regressions": 0,
  "decision": "PARTIALLY_VERIFIED",
  "reason": "Progress made: 1 failure resolved, 2 failures remaining.",
  "next_action": "REINVESTIGATE",
  "validation_summary": "Patch successful for targeted bug. 19 passed, 2 failed. Continuing to next defect."
}
```

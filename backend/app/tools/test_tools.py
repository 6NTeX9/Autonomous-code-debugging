import json
import re
from typing import Optional, Dict, Any, List
from app.tools.tool_context import ToolContext
from app.sandbox.sandbox_interface import ExecutionResult
from app.schemas.schemas import TestSuiteResult, TestFailure

async def run_command(ctx: ToolContext, command: str, timeout: Optional[int] = None) -> ExecutionResult:
    await ctx.emit_event("TOOL_CALL", tool="run_command", payload={"command": command})
    result = await ctx.sandbox.execute(command=command, cwd=str(ctx.workspace_path), timeout=timeout)
    await ctx.emit_event(
        "TOOL_RESULT",
        tool="run_command",
        payload={
            "command": command,
            "exit_code": result.exit_code,
            "duration_ms": result.duration_ms,
            "timed_out": result.timed_out
        }
    )
    return result

async def run_tests(ctx: ToolContext, custom_command: Optional[str] = None) -> ExecutionResult:
    await ctx.emit_event("TEST_STARTED", tool="run_tests")

    # Determine command
    cmd = custom_command
    if not cmd:
        ws = ctx.workspace_path
        if (ws / "package.json").exists():
            cmd = "npm test"
        elif (ws / "requirements.txt").exists() or (ws / "pyproject.toml").exists():
            cmd = "pytest"
        else:
            cmd = "npm test"

    result = await ctx.sandbox.execute(command=cmd, cwd=str(ctx.workspace_path))
    await ctx.emit_event(
        "TEST_COMPLETED",
        tool="run_tests",
        payload={
            "command": cmd,
            "exit_code": result.exit_code,
            "duration_ms": result.duration_ms
        },
        message=f"Test run completed with exit code {result.exit_code} in {result.duration_ms}ms"
    )
    return result

def _parse_jest_output(combined_output: str) -> TestSuiteResult:
    total = 0
    passed = 0
    failed = 0
    skipped = 0
    failures: List[TestFailure] = []

    # Try JSON output first if Jest was run with --json
    try:
        json_match = re.search(r"(\{.*\"testResults\":.*\})", combined_output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            total = data.get("numTotalTests", 0)
            passed = data.get("numPassedTests", 0)
            failed = data.get("numFailedTests", 0)
            skipped = data.get("numPendingTests", 0)

            for suite in data.get("testResults", []):
                for assertion in suite.get("assertionResults", []):
                    if assertion.get("status") == "failed":
                        msg = "\n".join(assertion.get("failureMessages", []))
                        failures.append(TestFailure(
                            test=assertion.get("title", "Unknown test"),
                            error=msg[:500] if msg else "Assertion failed",
                            file=suite.get("name")
                        ))
            return TestSuiteResult(
                total=total,
                passed=passed,
                failed=failed,
                skipped=skipped,
                failures=failures
            )
    except Exception:
        pass

    # Regex parse standard Jest output
    # Tests:       3 failed, 18 passed, 21 total
    tests_summary = re.search(r"Tests:\s+([^\n]+)", combined_output)
    if tests_summary:
        line = tests_summary.group(1)
        failed_m = re.search(r"(\d+)\s+failed", line)
        passed_m = re.search(r"(\d+)\s+passed", line)
        skipped_m = re.search(r"(\d+)\s+skipped|todo", line)
        total_m = re.search(r"(\d+)\s+total", line)

        failed = int(failed_m.group(1)) if failed_m else 0
        passed = int(passed_m.group(1)) if passed_m else 0
        skipped = int(skipped_m.group(1)) if skipped_m else 0
        total = int(total_m.group(1)) if total_m else (passed + failed + skipped)

    # Extract individual failure blocks
    fail_blocks = re.split(r"●\s+", combined_output)[1:]
    for block in fail_blocks:
        lines = block.strip().split("\n")
        if lines:
            test_title = lines[0].strip()
            error_body = "\n".join(lines[1:8]).strip()
            
            # Find file/line if available
            file_m = re.search(r"at\s+.*\(([^:]+):(\d+):(\d+)\)", block)
            file_name = file_m.group(1) if file_m else None
            line_no = int(file_m.group(2)) if file_m else None

            failures.append(TestFailure(
                test=test_title,
                error=error_body[:400],
                file=file_name,
                line=line_no
            ))

    # If nothing matched summary line but exit code was 0
    if total == 0 and "PASS" in combined_output:
        passed_matches = len(re.findall(r"✓\s+", combined_output))
        passed = max(passed_matches, 1)
        total = passed

    return TestSuiteResult(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        failures=failures
    )

def _parse_pytest_output(combined_output: str) -> TestSuiteResult:
    total = 0
    passed = 0
    failed = 0
    failures: List[TestFailure] = []

    # 18 passed, 3 failed in 0.5s
    summary = re.search(r"===\s+(.*?)\s+in\s+[\d\.]+s\s+===", combined_output)
    if summary:
        line = summary.group(1)
        passed_m = re.search(r"(\d+)\s+passed", line)
        failed_m = re.search(r"(\d+)\s+failed", line)
        passed = int(passed_m.group(1)) if passed_m else 0
        failed = int(failed_m.group(1)) if failed_m else 0
        total = passed + failed

    # Extract pytest failures
    fail_sections = re.findall(r"_{3,}\s+([^\n_]+)\s+_{3,}(.*?)(?=(?:_{3,}|\Z))", combined_output, re.DOTALL)
    for title, body in fail_sections:
        failures.append(TestFailure(
            test=title.strip(),
            error=body.strip()[:400]
        ))

    return TestSuiteResult(
        total=total,
        passed=passed,
        failed=failed,
        skipped=0,
        failures=failures
    )

async def get_test_results(ctx: ToolContext, execution: ExecutionResult) -> TestSuiteResult:
    await ctx.emit_event("TOOL_CALL", tool="get_test_results")
    combined = f"{execution.stdout}\n{execution.stderr}"

    if "pytest" in execution.command.lower() or "===" in combined:
        res = _parse_pytest_output(combined)
    else:
        res = _parse_jest_output(combined)

    res.stdout = execution.stdout
    res.stderr = execution.stderr

    await ctx.emit_event(
        "TOOL_RESULT",
        tool="get_test_results",
        payload={
            "total": res.total,
            "passed": res.passed,
            "failed": res.failed,
            "failures_count": len(res.failures)
        },
        message=f"Parsed test results: {res.passed} passed, {res.failed} failed of {res.total} total"
    )
    return res

async def inspect_error_log(ctx: ToolContext, error_log: str) -> Dict[str, Any]:
    await ctx.emit_event("TOOL_CALL", tool="inspect_error_log")

    error_types = set(re.findall(r"([A-Za-z]+Error):", error_log))
    stack_frames = re.findall(r"at\s+([^\n]+)", error_log)
    referenced_files = set(re.findall(r"([a-zA-Z0-9_\-\.\/]+\.(?:ts|js|py)):(\d+)", error_log))

    parsed = {
        "error_types": list(error_types),
        "stack_frames": stack_frames[:10],
        "referenced_files": [{"file": f, "line": int(l)} for f, l in referenced_files]
    }

    await ctx.emit_event("TOOL_RESULT", tool="inspect_error_log", payload=parsed)
    return parsed

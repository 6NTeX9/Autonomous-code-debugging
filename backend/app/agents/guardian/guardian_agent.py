import logging
from typing import Optional, Dict, Any, List
from app.tools.tool_context import ToolContext
from app.tools import run_tests, get_test_results, get_git_diff, rollback_changes
from app.schemas.schemas import RepairerOutput, GuardianOutput, TestSuiteResult

logger = logging.getLogger("debugging_agent.agents.guardian")

class GuardianAgent:
    async def run(
        self,
        ctx: ToolContext,
        patch_info: RepairerOutput,
        tests_before: TestSuiteResult
    ) -> GuardianOutput:
        ctx.current_agent = "GUARDIAN"
        await ctx.emit_event(
            "AGENT_STARTED",
            message=f"Guardian Agent initiated: Validating patch {patch_info.patch_id} against test suite"
        )

        # 1. Run complete test suite after patch
        test_exec = await run_tests(ctx)
        tests_after = await get_test_results(ctx, test_exec)

        # 2. Check for regressions
        # A regression occurs if the number of passed tests decreased or previously passing tests failed
        regressions = 0
        if tests_after.passed < tests_before.passed:
            regressions = tests_before.passed - tests_after.passed

        # Check outcome
        decision = "PATCH_REJECTED"
        next_action = "REINVESTIGATE"
        reason = ""

        if tests_after.failed == 0 and tests_after.passed > 0:
            decision = "PATCH_VERIFIED"
            next_action = "PROCEED_TO_REPORT"
            reason = f"All {tests_after.total} tests passing. Zero failures remaining."
            validation_summary = f"All tests passed: {tests_after.passed}/{tests_after.total} passing (0 regressions)."

        elif regressions > 0:
            decision = "PATCH_REJECTED"
            next_action = "REINVESTIGATE"
            reason = f"Patch introduced {regressions} test regression(s). Rolling back changes."
            validation_summary = f"Regression detected: {regressions} previously passing tests failed. Rolling back to {patch_info.checkpoint}."
            
            # Rollback
            await ctx.emit_event(
                "PATCH_REJECTED",
                payload={"reason": reason, "regressions": regressions},
                message=reason
            )
            await rollback_changes(ctx, patch_info.checkpoint)

        elif tests_after.failed < tests_before.failed:
            # Partial progress made!
            fixed_count = tests_before.failed - tests_after.failed
            decision = "PARTIALLY_VERIFIED"
            next_action = "REINVESTIGATE"
            reason = f"Progress made: {fixed_count} failure(s) resolved, {tests_after.failed} failure(s) remaining."
            validation_summary = f"Patch successful for targeted bug. {tests_after.passed} passed, {tests_after.failed} failed. Continuing to next defect."

        else:
            # No progress or syntax error
            decision = "PATCH_REJECTED"
            next_action = "REINVESTIGATE"
            reason = f"Patch did not resolve failing tests ({tests_after.failed} failures remain). Rolling back."
            validation_summary = f"Validation failed: failures unchanged. Rolling back to {patch_info.checkpoint}."
            
            await ctx.emit_event(
                "PATCH_REJECTED",
                payload={"reason": reason},
                message=reason
            )
            await rollback_changes(ctx, patch_info.checkpoint)

        output = GuardianOutput(
            session_id=ctx.session_id,
            iteration=ctx.iteration,
            tests_before=tests_before,
            tests_after=tests_after,
            regressions=regressions,
            decision=decision,
            reason=reason,
            next_action=next_action,
            validation_summary=validation_summary
        )

        await ctx.emit_event(
            "AGENT_COMPLETED",
            payload={"output": output.model_dump()},
            message=f"Guardian Agent evaluation: {decision} ({validation_summary})"
        )

        return output

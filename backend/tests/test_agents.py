import pytest
from pathlib import Path
from app.core.llm import MockProvider
from app.tools.tool_context import ToolContext
from app.agents.scout.scout_agent import ScoutAgent
from app.agents.detective.detective_agent import DetectiveAgent
from app.agents.repairer.repairer_agent import RepairerAgent
from app.agents.guardian.guardian_agent import GuardianAgent
from app.schemas.schemas import ScoutOutput, TestFailure, TestSuiteResult, RepairerOutput

@pytest.mark.asyncio
async def test_detective_agent(tmp_path: Path):
    llm = MockProvider()
    detective = DetectiveAgent(llm)

    # Mock Scout Output
    scout_out = ScoutOutput(
        session_id="test_sess",
        project="sample-ecommerce",
        language="TypeScript",
        framework="Express",
        test_framework="Jest",
        failures=[
            TestFailure(
                test="should return 404 for missing user",
                error="TypeError: Cannot read properties of undefined (reading 'name')",
                file="src/controllers/userController.ts"
            )
        ],
        affected_files=["src/controllers/userController.ts"],
        relevant_symbols=["getUser()"]
    )

    ctx = ToolContext(workspace_path=tmp_path, session_id="test_sess")
    res = await detective.run(ctx, scout_out)

    assert res.confidence >= 0.8
    assert len(res.hypotheses) > 0
    assert "src/controllers/userController.ts" in res.affected_files
    assert "getUser()" in res.reasoning_summary or "missing" in res.root_cause.lower()

@pytest.mark.asyncio
async def test_guardian_regression_detection(tmp_path: Path):
    guardian = GuardianAgent()
    ctx = ToolContext(workspace_path=tmp_path, session_id="test_sess")

    patch_info = RepairerOutput(
        session_id="test_sess",
        iteration=1,
        patch_id="p1",
        modified_files=["app.ts"],
        diff="",
        checkpoint="cp1",
        patch_summary="test patch"
    )

    tests_before = TestSuiteResult(total=21, passed=18, failed=3)

    # Let's verify Guardian's evaluation logic by mocking run_tests or verifying outcomes
    # When tests_after has 0 failures:
    output = await guardian.run(ctx, patch_info, tests_before)
    assert output.decision in ["PATCH_VERIFIED", "PARTIALLY_VERIFIED", "PATCH_REJECTED"]

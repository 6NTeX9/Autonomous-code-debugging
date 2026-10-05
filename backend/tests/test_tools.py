import pytest
import os
from pathlib import Path
from app.tools.tool_context import ToolContext
from app.tools.filesystem_tools import list_files, read_file, search_code, get_file_metadata
from app.tools.git_tools import create_git_checkpoint, apply_patch, get_git_diff, rollback_changes, ensure_git_repo
from app.tools.test_tools import _parse_jest_output
from app.sandbox.process_driver import ProcessSandboxDriver

@pytest.mark.asyncio
async def test_filesystem_tools(tmp_path: Path):
    test_file = tmp_path / "hello.ts"
    test_file.write_text("export function greet() { return 'hello world'; }\n", encoding="utf-8")

    ctx = ToolContext(workspace_path=tmp_path, session_id="test_sess", sandbox=ProcessSandboxDriver(tmp_path))

    files = await list_files(ctx, ".")
    assert len(files) == 1
    assert files[0]["path"] == "hello.ts"

    content = await read_file(ctx, "hello.ts")
    assert "greet" in content

    matches = await search_code(ctx, "greet")
    assert len(matches) == 1
    assert matches[0]["file"] == "hello.ts"

    meta = await get_file_metadata(ctx, "hello.ts")
    assert meta["lines"] == 1
    assert meta["exists"] is True

@pytest.mark.asyncio
async def test_git_checkpoint_and_rollback(tmp_path: Path):
    ctx = ToolContext(workspace_path=tmp_path, session_id="test_sess", sandbox=ProcessSandboxDriver(tmp_path))
    
    file_a = tmp_path / "app.js"
    file_a.write_text("console.log('original');\n", encoding="utf-8")

    await ensure_git_repo(ctx)
    checkpoint = await create_git_checkpoint(ctx, "test_checkpoint")
    assert checkpoint == "test_checkpoint"

    # Modify file
    file_a.write_text("console.log('modified');\n", encoding="utf-8")
    diff = await get_git_diff(ctx, checkpoint)
    assert "-console.log('original');" in diff
    assert "+console.log('modified');" in diff

    # Rollback
    rollback_res = await rollback_changes(ctx, checkpoint)
    assert rollback_res["status"] == "ROLLED_BACK"

    # Verify original restored
    restored_content = file_a.read_text(encoding="utf-8")
    assert "original" in restored_content
    assert "modified" not in restored_content

def test_jest_output_parser():
    sample_jest_output = """
FAIL tests/user.test.ts
  ● UserController Tests › should return 404 for missing user
    TypeError: Cannot read properties of undefined (reading 'name')
      at UserController.getUser (src/controllers/userController.ts:21:23)

Tests:       1 failed, 20 passed, 21 total
Time:        1.2s
"""
    result = _parse_jest_output(sample_jest_output)
    assert result.total == 21
    assert result.passed == 20
    assert result.failed == 1
    assert len(result.failures) == 1
    assert "should return 404 for missing user" in result.failures[0].test

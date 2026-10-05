import pytest
import os
from pathlib import Path
from app.sandbox.process_driver import ProcessSandboxDriver
from app.sandbox.security import validate_safe_path, SecurityViolationError

@pytest.mark.asyncio
async def test_sandbox_safe_execution(tmp_path: Path):
    driver = ProcessSandboxDriver(workspace_root=tmp_path)
    result = await driver.execute("echo 'Hello Sandbox'", cwd=str(tmp_path))
    assert result.exit_code == 0
    assert "Hello Sandbox" in result.stdout
    assert not result.timed_out

@pytest.mark.asyncio
async def test_sandbox_timeout(tmp_path: Path):
    driver = ProcessSandboxDriver(workspace_root=tmp_path)
    result = await driver.execute("sleep 5", cwd=str(tmp_path), timeout=1)
    assert result.timed_out is True
    assert result.exit_code == -1

def test_sandbox_path_traversal_protection(tmp_path: Path):
    with pytest.raises(SecurityViolationError):
        validate_safe_path("../../etc/passwd", tmp_path)

def test_sandbox_env_sanitization(tmp_path: Path):
    os.environ["LLM_API_KEY"] = "secret-token-123"
    driver = ProcessSandboxDriver(workspace_root=tmp_path)
    env = driver._sanitize_env()
    assert "LLM_API_KEY" not in env

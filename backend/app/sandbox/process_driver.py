import asyncio
import os
import time
import logging
from pathlib import Path
from typing import Dict, Optional
from app.sandbox.sandbox_interface import SandboxDriver, ExecutionResult
from app.sandbox.security import validate_safe_path
from app.core.config import settings

logger = logging.getLogger("debugging_agent.sandbox.process")

# Sensitive environment variables to strip
SENSITIVE_ENV_VARS = {
    "LLM_API_KEY", "OPENAI_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
    "GITHUB_TOKEN", "DATABASE_URL", "SECRET_KEY"
}

class ProcessSandboxDriver(SandboxDriver):
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def _sanitize_env(self, custom_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        # Inherit basic path & shell variables, but strip sensitive tokens
        env = {
            k: v for k, v in os.environ.items()
            if k not in SENSITIVE_ENV_VARS
        }
        # Ensure standard paths are accessible
        env["PATH"] = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
        env["NODE_ENV"] = "test"
        env["CI"] = "true"
        if custom_env:
            for k, v in custom_env.items():
                if k not in SENSITIVE_ENV_VARS:
                    env[k] = v
        return env

    async def execute(
        self,
        command: str,
        cwd: str,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        # Validate that cwd is strictly within the workspace
        resolved_cwd = validate_safe_path(cwd, self.workspace_root)
        effective_timeout = timeout or settings.EXECUTION_TIMEOUT_SECONDS
        sanitized_env = self._sanitize_env(env)

        start_time = time.time()
        logger.info(f"Sandbox executing in {resolved_cwd}: {command} (timeout={effective_timeout}s)")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=str(resolved_cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=sanitized_env
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=effective_timeout
                )
                duration_ms = (time.time() - start_time) * 1000
                stdout = stdout_bytes.decode('utf-8', errors='replace')
                stderr = stderr_bytes.decode('utf-8', errors='replace')
                exit_code = process.returncode if process.returncode is not None else -1

                return ExecutionResult(
                    command=command,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    duration_ms=round(duration_ms, 2),
                    timed_out=False
                )

            except asyncio.TimeoutError:
                logger.warning(f"Command timed out after {effective_timeout}s: {command}")
                try:
                    process.kill()
                    await process.wait()
                except ProcessLookupError:
                    pass
                duration_ms = (time.time() - start_time) * 1000
                return ExecutionResult(
                    command=command,
                    stdout="",
                    stderr=f"Execution timed out after {effective_timeout} seconds.",
                    exit_code=-1,
                    duration_ms=round(duration_ms, 2),
                    timed_out=True
                )

        except Exception as e:
            logger.error(f"Process execution error: {e}", exc_info=True)
            duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                exit_code=-1,
                duration_ms=round(duration_ms, 2),
                timed_out=False
            )

    def cleanup(self) -> None:
        pass

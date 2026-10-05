import asyncio
import os
import time
import logging
from pathlib import Path
from typing import Dict, Optional
from app.sandbox.sandbox_interface import SandboxDriver, ExecutionResult
from app.sandbox.security import validate_safe_path
from app.core.config import settings

logger = logging.getLogger("debugging_agent.sandbox.docker")

class DockerSandboxDriver(SandboxDriver):
    def __init__(self, workspace_root: Path, image: str = "node:20-alpine"):
        self.workspace_root = workspace_root.resolve()
        self.image = image

    async def execute(
        self,
        command: str,
        cwd: str,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        resolved_cwd = validate_safe_path(cwd, self.workspace_root)
        rel_cwd = resolved_cwd.relative_to(self.workspace_root)
        container_workdir = f"/workspace/{rel_cwd}" if str(rel_cwd) != "." else "/workspace"
        effective_timeout = timeout or settings.EXECUTION_TIMEOUT_SECONDS

        start_time = time.time()

        docker_cmd = [
            "docker", "run", "--rm",
            "-i",
            "--memory=512m",
            "--cpus=1.5",
            "--pids-limit=100",
            "-v", f"{self.workspace_root}:/workspace",
            "-w", container_workdir,
            "-e", "CI=true",
            "-e", "NODE_ENV=test"
        ]

        if env:
            for k, v in env.items():
                docker_cmd.extend(["-e", f"{k}={v}"])

        docker_cmd.extend([self.image, "sh", "-c", command])

        try:
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
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
                try:
                    process.kill()
                    await process.wait()
                except ProcessLookupError:
                    pass
                duration_ms = (time.time() - start_time) * 1000
                return ExecutionResult(
                    command=command,
                    stdout="",
                    stderr=f"Docker container execution timed out after {effective_timeout}s.",
                    exit_code=-1,
                    duration_ms=round(duration_ms, 2),
                    timed_out=True
                )

        except Exception as e:
            logger.error(f"Docker sandbox error: {e}")
            duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"Docker execution failed: {str(e)}",
                exit_code=-1,
                duration_ms=round(duration_ms, 2),
                timed_out=False
            )

    def cleanup(self) -> None:
        pass

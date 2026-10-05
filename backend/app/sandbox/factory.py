import shutil
import subprocess
import logging
from pathlib import Path
from app.sandbox.sandbox_interface import SandboxDriver
from app.sandbox.process_driver import ProcessSandboxDriver
from app.sandbox.docker_driver import DockerSandboxDriver
from app.core.config import settings

logger = logging.getLogger("debugging_agent.sandbox.factory")

def is_docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        return res.returncode == 0
    except Exception:
        return False

def get_sandbox_driver(workspace_root: Path) -> SandboxDriver:
    if settings.SANDBOX_TYPE == "docker":
        if is_docker_available():
            logger.info("Using DockerSandboxDriver")
            return DockerSandboxDriver(workspace_root=workspace_root)
        else:
            logger.warning("Docker requested but daemon is not available. Falling back to ProcessSandboxDriver.")
            return ProcessSandboxDriver(workspace_root=workspace_root)
    elif settings.SANDBOX_TYPE == "auto":
        if is_docker_available():
            logger.info("Docker daemon detected. Using DockerSandboxDriver.")
            return DockerSandboxDriver(workspace_root=workspace_root)
        else:
            logger.info("Docker daemon unavailable. Using secure ProcessSandboxDriver.")
            return ProcessSandboxDriver(workspace_root=workspace_root)
    else:
        return ProcessSandboxDriver(workspace_root=workspace_root)

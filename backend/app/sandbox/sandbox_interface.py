from abc import ABC, abstractmethod
from typing import Dict, Optional
from pydantic import BaseModel

class ExecutionResult(BaseModel):
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    timed_out: bool = False

class SandboxDriver(ABC):
    @abstractmethod
    async def execute(
        self,
        command: str,
        cwd: str,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

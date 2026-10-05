import logging
from pathlib import Path
from typing import Callable, Optional, Any, Dict
from app.sandbox.sandbox_interface import SandboxDriver
from app.sandbox.factory import get_sandbox_driver

logger = logging.getLogger("debugging_agent.tools.context")

# Callback type: (agent_name, event_type, tool_name, payload, message) -> None
EventEmitter = Callable[[str, str, Optional[str], Optional[Dict[str, Any]], Optional[str]], Any]

class ToolContext:
    def __init__(
        self,
        workspace_path: Path,
        session_id: str,
        current_agent: str = "SCOUT",
        iteration: int = 1,
        event_emitter: Optional[EventEmitter] = None,
        sandbox: Optional[SandboxDriver] = None
    ):
        self.workspace_path = workspace_path.resolve()
        self.session_id = session_id
        self.current_agent = current_agent
        self.iteration = iteration
        self.event_emitter = event_emitter
        self.sandbox = sandbox or get_sandbox_driver(self.workspace_path)

    async def emit_event(
        self,
        event_type: str,
        tool: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> None:
        if self.event_emitter:
            try:
                res = self.event_emitter(self.current_agent, event_type, tool, payload, message)
                if hasattr(res, "__await__"):
                    await res
            except Exception as e:
                logger.error(f"Error in event_emitter: {e}")

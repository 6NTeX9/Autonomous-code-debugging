from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# --- Event Schemas ---
class AgentEventCreate(BaseModel):
    agent: str
    event: str
    iteration: int = 1
    tool: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class AgentEventResponse(BaseModel):
    id: str
    session_id: str
    agent: str
    event: str
    iteration: int
    tool: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# --- Scout Schemas ---
class TestFailure(BaseModel):
    test: str
    error: str
    file: Optional[str] = None
    line: Optional[int] = None

class ScoutOutput(BaseModel):
    session_id: str
    project: str
    language: str
    framework: Optional[str] = None
    test_framework: Optional[str] = None
    source_dirs: List[str] = []
    test_dirs: List[str] = []
    entry_points: List[str] = []
    dependencies: List[str] = []
    initial_test_summary: Dict[str, Any] = {}
    failures: List[TestFailure] = []
    stack_trace: Optional[str] = None
    affected_files: List[str] = []
    relevant_symbols: List[str] = []
    raw_error_log: Optional[str] = None

# --- Detective Schemas ---
class HypothesisItem(BaseModel):
    description: str
    evidence: List[str] = []
    affected_files: List[str] = []
    confidence: float = 0.0

class DetectiveOutput(BaseModel):
    session_id: str
    iteration: int
    hypotheses: List[HypothesisItem] = []
    root_cause: str
    evidence: List[str] = []
    affected_files: List[str] = []
    confidence: float
    repair_strategy: str
    constraints: List[str] = []
    reasoning_summary: str  # Concise, evidence-based reasoning without hidden CoT

# --- Repairer Schemas ---
class FilePatch(BaseModel):
    path: str
    diff: str
    new_content: Optional[str] = None

class RepairerOutput(BaseModel):
    session_id: str
    iteration: int
    patch_id: str
    modified_files: List[str]
    diff: str
    checkpoint: str
    patch_summary: str

# --- Guardian Schemas ---
class TestSuiteResult(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    failures: List[TestFailure] = []
    stdout: Optional[str] = None
    stderr: Optional[str] = None

class GuardianOutput(BaseModel):
    session_id: str
    iteration: int
    tests_before: TestSuiteResult
    tests_after: TestSuiteResult
    regressions: int
    decision: str  # "PATCH_VERIFIED" or "PATCH_REJECTED"
    reason: str
    next_action: str  # "PROCEED_TO_REPORT" or "REINVESTIGATE"
    validation_summary: str

# --- Project & Session Schemas ---
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    test_framework: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    test_framework: Optional[str] = None
    workspace_path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StartDebugRequest(BaseModel):
    mode: str = "AUTO"  # "AUTO" or "APPROVAL_REQUIRED"
    max_iterations: int = 5

class SessionResponse(BaseModel):
    id: str
    project_id: str
    status: str
    current_agent: str
    mode: str
    iteration: int
    max_iterations: int
    current_error: Optional[str] = None
    stack_trace: Optional[str] = None
    active_checkpoint: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DebugReportResponse(BaseModel):
    id: str
    session_id: str
    project_name: str
    language: Optional[str] = None
    framework: Optional[str] = None
    status: str
    original_error: Optional[str] = None
    root_cause: Optional[str] = None
    evidence: List[str] = []
    affected_files: List[str] = []
    files_modified: List[str] = []
    patch_summary: Optional[str] = None
    tests_before: Dict[str, Any] = {}
    tests_after: Dict[str, Any] = {}
    iterations: int
    regressions: int
    validation_result: str
    confidence: str
    remaining_issues: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

class HumanDecisionRequest(BaseModel):
    action: str  # "APPROVE", "REJECT", "CANCEL"
    feedback: Optional[str] = None

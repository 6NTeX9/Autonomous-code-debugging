import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    framework = Column(String(50), nullable=True)
    test_framework = Column(String(50), nullable=True)
    workspace_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    sessions = relationship("DebugSession", back_populates="project", cascade="all, delete-orphan")

class DebugSession(Base):
    __tablename__ = "debug_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    status = Column(String(50), default="INITIALIZING")  # INITIALIZING, ANALYZING_REPOSITORY, etc.
    current_agent = Column(String(50), default="SCOUT")  # SCOUT, DETECTIVE, REPAIRER, GUARDIAN
    mode = Column(String(20), default="AUTO")  # AUTO, APPROVAL_REQUIRED
    iteration = Column(Integer, default=1)
    max_iterations = Column(Integer, default=5)
    
    # State fields
    current_error = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    active_checkpoint = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="sessions")
    events = relationship("AgentEvent", back_populates="session", cascade="all, delete-orphan")
    errors = relationship("ErrorRecord", back_populates="session", cascade="all, delete-orphan")
    hypotheses = relationship("Hypothesis", back_populates="session", cascade="all, delete-orphan")
    patches = relationship("Patch", back_populates="session", cascade="all, delete-orphan")
    test_runs = relationship("TestRun", back_populates="session", cascade="all, delete-orphan")
    report = relationship("DebugReport", back_populates="session", uselist=False, cascade="all, delete-orphan")

class AgentEvent(Base):
    __tablename__ = "agent_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("debug_sessions.id"), nullable=False)
    agent = Column(String(50), nullable=False)  # SCOUT, DETECTIVE, REPAIRER, GUARDIAN, ORCHESTRATOR
    event = Column(String(50), nullable=False)  # TOOL_CALL, TOOL_RESULT, ROOT_CAUSE_IDENTIFIED, etc.
    iteration = Column(Integer, default=1)
    tool = Column(String(100), nullable=True)
    payload = Column(JSON, nullable=True)
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now)

    session = relationship("DebugSession", back_populates="events")

class ErrorRecord(Base):
    __tablename__ = "error_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("debug_sessions.id"), nullable=False)
    iteration = Column(Integer, default=1)
    error_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    failing_test = Column(String(255), nullable=True)
    affected_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("DebugSession", back_populates="errors")

class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("debug_sessions.id"), nullable=False)
    iteration = Column(Integer, default=1)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default=list)  # list of strings
    affected_files = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("DebugSession", back_populates="hypotheses")

class Patch(Base):
    __tablename__ = "patches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("debug_sessions.id"), nullable=False)
    iteration = Column(Integer, default=1)
    patch_id = Column(String(100), nullable=False)
    modified_files = Column(JSON, default=list)
    diff = Column(Text, nullable=False)
    checkpoint = Column(String(255), nullable=True)
    patch_summary = Column(Text, nullable=False)
    status = Column(String(50), default="APPLIED")  # APPLIED, VALIDATED, REJECTED, ROLLED_BACK
    created_at = Column(DateTime, default=utc_now)

    session = relationship("DebugSession", back_populates="patches")

class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("debug_sessions.id"), nullable=False)
    iteration = Column(Integer, default=1)
    phase = Column(String(50), default="INITIAL")  # INITIAL, VALIDATION
    total = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    regressions = Column(Integer, default=0)
    details = Column(JSON, default=dict)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    passed_all = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=utc_now)

    session = relationship("DebugSession", back_populates="test_runs")

class DebugReport(Base):
    __tablename__ = "debug_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("debug_sessions.id"), unique=True, nullable=False)
    project_name = Column(String(255), nullable=False)
    language = Column(String(50), nullable=True)
    framework = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False)  # SUCCESS, FAILED, HUMAN_INTERVENTION_REQUIRED
    original_error = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    evidence = Column(JSON, default=list)
    affected_files = Column(JSON, default=list)
    files_modified = Column(JSON, default=list)
    patch_summary = Column(Text, nullable=True)
    tests_before = Column(JSON, default=dict)
    tests_after = Column(JSON, default=dict)
    iterations = Column(Integer, default=1)
    regressions = Column(Integer, default=0)
    validation_result = Column(String(50), default="VERIFIED")
    confidence = Column(String(20), default="High")
    remaining_issues = Column(JSON, default=list)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("DebugSession", back_populates="report")

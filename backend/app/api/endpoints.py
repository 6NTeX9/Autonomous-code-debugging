import asyncio
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.models.database_models import (
    Project, DebugSession, AgentEvent, ErrorRecord,
    Hypothesis, Patch, TestRun, DebugReport
)
from app.schemas.schemas import (
    ProjectResponse, SessionResponse, AgentEventResponse,
    DebugReportResponse, StartDebugRequest, HumanDecisionRequest
)
from app.services.project_service import ProjectService
from app.orchestrator.orchestrator import (
    Orchestrator, approval_events, approval_decisions, cancellation_flags
)
from app.api.websocket_manager import ws_manager
from app.tools.tool_context import ToolContext
from app.tools.git_tools import get_git_diff, rollback_changes

logger = logging.getLogger("debugging_agent.api")
router = APIRouter()

# --- Projects Endpoints ---

@router.post("/projects/upload", response_model=ProjectResponse)
async def upload_project(
    name: str = Form(...),
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        project = await ProjectService.create_project_from_upload(
            db=db,
            name=name,
            upload_file=file,
            description=description
        )
        return project
    except Exception as e:
        logger.error(f"Failed to upload project: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/projects/sample", response_model=ProjectResponse)
def load_sample_project(db: Session = Depends(get_db)):
    try:
        project = ProjectService.create_project_from_sample(db)
        return project
    except Exception as e:
        logger.error(f"Failed to load sample project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/projects/{project_id}/download")
def download_repaired_project(project_id: str, db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse
    import zipfile
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or not Path(project.workspace_path).exists():
        raise HTTPException(status_code=404, detail="Project workspace not found")

    ws_path = Path(project.workspace_path)
    zip_path = ws_path.parent / f"{project.name}-repaired.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in ws_path.rglob("*"):
            if any(part in file.parts for part in ["node_modules", ".git", "__pycache__", ".venv", ".next"]):
                continue
            if file.is_file() and file != zip_path:
                zipf.write(file, file.relative_to(ws_path))

    return FileResponse(
        path=str(zip_path),
        filename=f"{project.name}-repaired.zip",
        media_type="application/zip"
    )

# --- Debug Session Endpoints ---

@router.post("/debug/{project_id}/start", response_model=SessionResponse)
async def start_debug_session(
    project_id: str,
    req: StartDebugRequest,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    session = DebugSession(
        project_id=project.id,
        status="INITIALIZING",
        current_agent="SCOUT",
        mode=req.mode,
        iteration=1,
        max_iterations=req.max_iterations
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    session_id = session.id

    # Spawn orchestrator in background task
    async def run_pipeline():
        try:
            orch = Orchestrator(session_id=session_id)
            await orch.execute_debugging_pipeline()
        except Exception as ex:
            logger.error(f"Pipeline execution error for session {session_id}: {ex}", exc_info=True)
            async_db = SessionLocal()
            try:
                s = async_db.query(DebugSession).filter(DebugSession.id == session_id).first()
                if s:
                    s.status = "FAILED"
                    async_db.commit()
            finally:
                async_db.close()

    asyncio.create_task(run_pipeline())

    return session

@router.get("/debug/{session_id}/status", response_model=SessionResponse)
def get_debug_status(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DebugSession).filter(DebugSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/debug/{session_id}/events", response_model=List[AgentEventResponse])
def get_debug_events(session_id: str, db: Session = Depends(get_db)):
    events = (
        db.query(AgentEvent)
        .filter(AgentEvent.session_id == session_id)
        .order_by(AgentEvent.timestamp.asc())
        .all()
    )
    return events

@router.get("/debug/{session_id}/logs")
def get_debug_logs(session_id: str, db: Session = Depends(get_db)):
    runs = (
        db.query(TestRun)
        .filter(TestRun.session_id == session_id)
        .order_by(TestRun.timestamp.asc())
        .all()
    )
    return [
        {
            "iteration": r.iteration,
            "phase": r.phase,
            "passed": r.passed,
            "failed": r.failed,
            "stdout": r.stdout,
            "stderr": r.stderr
        }
        for r in runs
    ]

@router.get("/debug/{session_id}/diff")
async def get_session_diff(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DebugSession).filter(DebugSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get latest patch diff if recorded
    latest_patch = (
        db.query(Patch)
        .filter(Patch.session_id == session_id)
        .order_by(Patch.created_at.desc())
        .first()
    )

    ctx = ToolContext(workspace_path=Path(project.workspace_path), session_id=session_id)
    git_diff_text = await get_git_diff(ctx)

    return {
        "patch_id": latest_patch.patch_id if latest_patch else None,
        "modified_files": latest_patch.modified_files if latest_patch else [],
        "summary": latest_patch.patch_summary if latest_patch else None,
        "diff": git_diff_text or (latest_patch.diff if latest_patch else "")
    }

@router.get("/debug/{session_id}/report", response_model=DebugReportResponse)
def get_debug_report(session_id: str, db: Session = Depends(get_db)):
    report = db.query(DebugReport).filter(DebugReport.session_id == session_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    return report

@router.post("/debug/{session_id}/cancel")
def cancel_debug_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DebugSession).filter(DebugSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    cancellation_flags[session_id] = True
    session.status = "CANCELLED"
    db.commit()

    if session_id in approval_events:
        approval_decisions[session_id] = {"action": "CANCEL"}
        approval_events[session_id].set()

    return {"status": "CANCELLED", "session_id": session_id}

@router.post("/debug/{session_id}/rollback")
async def manual_rollback(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DebugSession).filter(DebugSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    project = db.query(Project).filter(Project.id == session.project_id).first()

    ctx = ToolContext(workspace_path=Path(project.workspace_path), session_id=session_id)
    res = await rollback_changes(ctx, session.active_checkpoint)
    return res

@router.post("/debug/{session_id}/decide")
def submit_human_decision(
    session_id: str,
    decision: HumanDecisionRequest,
    db: Session = Depends(get_db)
):
    session = db.query(DebugSession).filter(DebugSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    approval_decisions[session_id] = {
        "action": decision.action.upper(),
        "feedback": decision.feedback
    }

    if session_id in approval_events:
        approval_events[session_id].set()

    return {"status": "DECISION_RECORDED", "decision": decision.action}

# --- WebSocket Endpoint ---

@router.websocket("/ws/debug/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            # Keep connection open; receive client pings/messages if sent
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
    except Exception:
        ws_manager.disconnect(session_id, websocket)

import pytest
import shutil
from pathlib import Path
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.project_service import ProjectService
from app.models.database_models import DebugSession, Project, Patch, TestRun, DebugReport
from app.orchestrator.orchestrator import Orchestrator

@pytest.mark.asyncio
async def test_full_autonomous_debugging_pipeline(tmp_path: Path):
    """
    Complete Autonomous Multi-Agent Loop E2E Test:
    Buggy Project (18 passed / 3 failed)
    -> Scout -> Detective -> Repairer -> Guardian
    -> Iteration 1 (19 passed / 2 failed)
    -> Iteration 2 (20 passed / 1 failed)
    -> Iteration 3 (21 passed / 0 failed) -> SUCCESS
    -> Final Verified Autonomous Debugging Report
    """
    db = SessionLocal()
    try:
        # 1. Initialize fresh copy of sample project in test directory
        project = ProjectService.create_project_from_sample(db, sample_dir=settings.SAMPLE_PROJECT_DIR)
        assert project.id is not None

        # 2. Create DebugSession in AUTO mode
        session = DebugSession(
            project_id=project.id,
            status="INITIALIZING",
            current_agent="SCOUT",
            mode="AUTO",
            iteration=1,
            max_iterations=5
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # 3. Execute Orchestrator pipeline
        orchestrator = Orchestrator(session_id=session.id, db=db)
        report = await orchestrator.execute_debugging_pipeline()

        # 4. Verify outcomes
        db.refresh(session)
        assert session.status == "FIXED"
        assert report.status == "SUCCESS"
        assert report.validation_result == "VERIFIED"
        assert report.tests_after["passed"] == 21
        assert report.tests_after["failed"] == 0
        assert report.regressions == 0
        assert report.iterations <= 5

        # Check patches recorded in DB
        patches = db.query(Patch).filter(Patch.session_id == session.id).all()
        assert len(patches) >= 1
        all_modified_files = [mf for p in patches for mf in (p.modified_files or [])]
        assert any("userController" in mf for mf in all_modified_files)

        # Check final report in DB
        db_report = db.query(DebugReport).filter(DebugReport.session_id == session.id).first()
        assert db_report is not None
        assert db_report.tests_after["passed"] == 21
        assert db_report.tests_after["failed"] == 0
        assert db_report.status == "SUCCESS"

    finally:
        db.close()

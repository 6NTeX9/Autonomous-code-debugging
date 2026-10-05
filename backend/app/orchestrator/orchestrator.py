import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.llm import get_llm_provider
from app.models.database_models import (
    Project, DebugSession, AgentEvent, ErrorRecord,
    Hypothesis, Patch, TestRun, DebugReport
)
from app.schemas.schemas import (
    ScoutOutput, DetectiveOutput, RepairerOutput, GuardianOutput,
    TestSuiteResult, TestFailure
)
from app.tools.tool_context import ToolContext
from app.agents.scout.scout_agent import ScoutAgent
from app.agents.detective.detective_agent import DetectiveAgent
from app.agents.repairer.repairer_agent import RepairerAgent
from app.agents.guardian.guardian_agent import GuardianAgent

logger = logging.getLogger("debugging_agent.orchestrator")

# Global dict of active orchestrator pause events for APPROVAL_REQUIRED mode: session_id -> asyncio.Event
approval_events: Dict[str, asyncio.Event] = {}
approval_decisions: Dict[str, Dict[str, Any]] = {}
cancellation_flags: Dict[str, bool] = {}

class Orchestrator:
    def __init__(self, session_id: str, db: Optional[Session] = None):
        self.session_id = session_id
        self._db = db
        self.llm = get_llm_provider()
        self.scout = ScoutAgent(self.llm)
        self.detective = DetectiveAgent(self.llm)
        self.repairer = RepairerAgent(self.llm)
        self.guardian = GuardianAgent()

    def get_db(self) -> Session:
        if self._db is not None:
            return self._db
        return SessionLocal()

    async def emit_agent_event(
        self,
        agent: str,
        event: str,
        tool: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> AgentEvent:
        db = self.get_db()
        try:
            session = db.query(DebugSession).filter(DebugSession.id == self.session_id).first()
            current_iter = session.iteration if session else 1

            event_record = AgentEvent(
                session_id=self.session_id,
                agent=agent,
                event=event,
                iteration=current_iter,
                tool=tool,
                payload=payload,
                message=message,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(event_record)
            db.commit()
            db.refresh(event_record)

            # Broadcast to real-time subscribers if any
            from app.api.websocket_manager import ws_manager
            await ws_manager.broadcast_to_session(self.session_id, {
                "id": event_record.id,
                "session_id": self.session_id,
                "agent": agent,
                "event": event,
                "iteration": current_iter,
                "tool": tool,
                "payload": payload,
                "message": message,
                "timestamp": event_record.timestamp.isoformat()
            })

            return event_record
        finally:
            if self._db is None:
                db.close()

    def check_cancelled(self) -> bool:
        return cancellation_flags.get(self.session_id, False)

    async def execute_debugging_pipeline(self) -> DebugReport:
        db = self.get_db()
        try:
            session = db.query(DebugSession).filter(DebugSession.id == self.session_id).first()
            if not session:
                raise ValueError(f"Session {self.session_id} not found")

            project = db.query(Project).filter(Project.id == session.project_id).first()
            if not project:
                raise ValueError(f"Project for session {self.session_id} not found")

            workspace_path = Path(project.workspace_path)
            cancellation_flags[self.session_id] = False

            # Create ToolContext
            ctx = ToolContext(
                workspace_path=workspace_path,
                session_id=self.session_id,
                current_agent="SCOUT",
                iteration=1,
                event_emitter=self.emit_agent_event
            )

            # Step 1: SCOUT starts initial investigation
            session.status = "ANALYZING_REPOSITORY"
            session.current_agent = "SCOUT"
            db.commit()

            scout_output = await self.scout.run(ctx, project_name=project.name)

            # Update project info in db if detected
            project.language = scout_output.language
            project.framework = scout_output.framework
            project.test_framework = scout_output.test_framework
            db.commit()

            # Record initial test run
            initial_run = TestRun(
                session_id=self.session_id,
                iteration=1,
                phase="INITIAL",
                total=scout_output.initial_test_summary.get("total", 0),
                passed=scout_output.initial_test_summary.get("passed", 0),
                failed=scout_output.initial_test_summary.get("failed", 0),
                details=scout_output.initial_test_summary,
                stdout=scout_output.stack_trace
            )
            db.add(initial_run)
            db.commit()

            # Record error entries
            for fail in scout_output.failures:
                err_rec = ErrorRecord(
                    session_id=self.session_id,
                    iteration=1,
                    error_type="AssertionFailure" if "Error" not in fail.error else fail.error.split(":")[0],
                    message=fail.error,
                    failing_test=fail.test,
                    affected_file=fail.file
                )
                db.add(err_rec)
            db.commit()

            # If no tests failed initially, we are already good!
            if scout_output.initial_test_summary.get("failed", 0) == 0:
                session.status = "FIXED"
                db.commit()
                return await self._generate_final_report(db, session, project, scout_output, None, None, 0)

            # Autonomous Iteration Loop (Max iterations = 5)
            max_iter = session.max_iterations or settings.MAX_ITERATIONS
            current_tests_state = TestSuiteResult(
                total=scout_output.initial_test_summary.get("total", 0),
                passed=scout_output.initial_test_summary.get("passed", 0),
                failed=scout_output.initial_test_summary.get("failed", 0),
                failures=scout_output.failures
            )

            last_detective_out: Optional[DetectiveOutput] = None
            last_repairer_out: Optional[RepairerOutput] = None
            last_guardian_out: Optional[GuardianOutput] = None
            total_regressions = 0

            for iteration in range(1, max_iter + 1):
                if self.check_cancelled():
                    session.status = "CANCELLED"
                    db.commit()
                    await self.emit_agent_event("ORCHESTRATOR", "DEBUGGING_CANCELLED", message="Session cancelled by user")
                    break

                session.iteration = iteration
                ctx.iteration = iteration
                db.commit()

                await self.emit_agent_event(
                    "ORCHESTRATOR",
                    "ITERATION_STARTED",
                    payload={"iteration": iteration, "max_iterations": max_iter},
                    message=f"Starting autonomous debugging iteration {iteration}/{max_iter}"
                )

                # -------------------------------------------------------------
                # AGENT 2: DETECTIVE
                # -------------------------------------------------------------
                session.status = "INVESTIGATING_ROOT_CAUSE"
                session.current_agent = "DETECTIVE"
                db.commit()

                detective_output = await self.detective.run(
                    ctx=ctx,
                    scout_findings=scout_output,
                    previous_guardian_feedback=last_guardian_out
                )
                last_detective_out = detective_output

                # Save hypotheses in DB
                for h in detective_output.hypotheses:
                    hyp_rec = Hypothesis(
                        session_id=self.session_id,
                        iteration=iteration,
                        description=h.description,
                        evidence=h.evidence,
                        affected_files=h.affected_files,
                        confidence=h.confidence,
                        is_selected=(h.confidence >= 0.8)
                    )
                    db.add(hyp_rec)
                db.commit()

                # -------------------------------------------------------------
                # AGENT 3: REPAIRER
                # -------------------------------------------------------------
                session.status = "GENERATING_PATCH"
                session.current_agent = "REPAIRER"
                db.commit()

                # Human-In-The-Loop Check (APPROVAL_REQUIRED)
                if session.mode == "APPROVAL_REQUIRED":
                    session.status = "WAITING_FOR_APPROVAL"
                    db.commit()
                    await self.emit_agent_event(
                        "ORCHESTRATOR",
                        "APPROVAL_REQUESTED",
                        payload={
                            "iteration": iteration,
                            "root_cause": detective_output.root_cause,
                            "repair_strategy": detective_output.repair_strategy,
                            "confidence": detective_output.confidence
                        },
                        message="Human approval required before applying patch. Pausing workflow."
                    )

                    # Wait for human approval signal
                    evt = asyncio.Event()
                    approval_events[self.session_id] = evt
                    await evt.wait()

                    decision = approval_decisions.get(self.session_id, {}).get("action", "APPROVE")
                    if decision == "REJECT":
                        await self.emit_agent_event("ORCHESTRATOR", "APPROVAL_REJECTED", message="Patch rejected by human operator")
                        continue
                    elif decision == "CANCEL":
                        session.status = "CANCELLED"
                        db.commit()
                        break

                repairer_output = await self.repairer.run(
                    ctx=ctx,
                    detective_diagnosis=detective_output
                )
                last_repairer_out = repairer_output
                session.active_checkpoint = repairer_output.checkpoint

                # Save Patch in DB
                patch_rec = Patch(
                    session_id=self.session_id,
                    iteration=iteration,
                    patch_id=repairer_output.patch_id,
                    modified_files=repairer_output.modified_files,
                    diff=repairer_output.diff,
                    checkpoint=repairer_output.checkpoint,
                    patch_summary=repairer_output.patch_summary,
                    status="APPLIED"
                )
                db.add(patch_rec)
                db.commit()

                # -------------------------------------------------------------
                # AGENT 4: GUARDIAN
                # -------------------------------------------------------------
                session.status = "VALIDATING_PATCH"
                session.current_agent = "GUARDIAN"
                db.commit()

                guardian_output = await self.guardian.run(
                    ctx=ctx,
                    patch_info=repairer_output,
                    tests_before=current_tests_state
                )
                last_guardian_out = guardian_output
                total_regressions += guardian_output.regressions

                # Save TestRun
                val_run = TestRun(
                    session_id=self.session_id,
                    iteration=iteration,
                    phase="VALIDATION",
                    total=guardian_output.tests_after.total,
                    passed=guardian_output.tests_after.passed,
                    failed=guardian_output.tests_after.failed,
                    regressions=guardian_output.regressions,
                    passed_all=(guardian_output.decision == "PATCH_VERIFIED")
                )
                db.add(val_run)

                # Update patch status based on Guardian decision
                if guardian_output.decision == "PATCH_VERIFIED":
                    patch_rec.status = "VALIDATED"
                elif guardian_output.decision == "PATCH_REJECTED":
                    patch_rec.status = "REJECTED"
                db.commit()

                await self.emit_agent_event(
                    "ORCHESTRATOR",
                    "ITERATION_COMPLETED",
                    payload={
                        "iteration": iteration,
                        "decision": guardian_output.decision,
                        "passed": guardian_output.tests_after.passed,
                        "failed": guardian_output.tests_after.failed
                    },
                    message=f"Iteration {iteration} evaluation: {guardian_output.decision}"
                )

                # Check if all tests pass
                if guardian_output.decision == "PATCH_VERIFIED":
                    session.status = "FIXED"
                    session.completed_at = datetime.now(timezone.utc)
                    db.commit()
                    await self.emit_agent_event(
                        "ORCHESTRATOR",
                        "DEBUGGING_COMPLETED",
                        payload={"status": "SUCCESS", "iterations": iteration},
                        message="All defects resolved. System verified 100% test pass rate."
                    )
                    return await self._generate_final_report(
                        db, session, project, scout_output, last_detective_out, last_repairer_out, iteration, total_regressions, "SUCCESS"
                    )

                # Update current_tests_state for next iteration
                if guardian_output.decision == "PARTIALLY_VERIFIED":
                    current_tests_state = guardian_output.tests_after
                    # Update scout_output failures so Detective focuses on remaining
                    scout_output.failures = guardian_output.tests_after.failures

            # If loop finished without resolution:
            session.status = "HUMAN_INTERVENTION_REQUIRED"
            session.completed_at = datetime.now(timezone.utc)
            db.commit()
            await self.emit_agent_event(
                "ORCHESTRATOR",
                "HUMAN_INTERVENTION_REQUIRED",
                payload={"iterations": max_iter},
                message=f"Reached maximum iteration limit ({max_iter}). Human intervention required."
            )

            return await self._generate_final_report(
                db, session, project, scout_output, last_detective_out, last_repairer_out, max_iter, total_regressions, "HUMAN_INTERVENTION_REQUIRED"
            )

        finally:
            if self._db is None:
                db.close()

    async def _generate_final_report(
        self,
        db: Session,
        session: DebugSession,
        project: Project,
        scout_output: ScoutOutput,
        detective_output: Optional[DetectiveOutput],
        repairer_output: Optional[RepairerOutput],
        iterations: int,
        regressions: int = 0,
        status: str = "SUCCESS"
    ) -> DebugReport:
        all_patches = db.query(Patch).filter(Patch.session_id == self.session_id).all()
        modified_files = set()
        patch_summaries = []
        for p in all_patches:
            for mf in (p.modified_files or []):
                modified_files.add(mf)
            if p.patch_summary:
                patch_summaries.append(p.patch_summary)

        # Get initial vs final test runs
        initial_test = db.query(TestRun).filter(TestRun.session_id == self.session_id, TestRun.phase == "INITIAL").first()
        latest_test = db.query(TestRun).filter(TestRun.session_id == self.session_id).order_by(TestRun.timestamp.desc()).first()

        tests_before = {
            "total": initial_test.total if initial_test else 0,
            "passed": initial_test.passed if initial_test else 0,
            "failed": initial_test.failed if initial_test else 0
        }
        tests_after = {
            "total": latest_test.total if latest_test else 0,
            "passed": latest_test.passed if latest_test else 0,
            "failed": latest_test.failed if latest_test else 0
        }

        report = DebugReport(
            session_id=self.session_id,
            project_name=project.name,
            language=project.language,
            framework=project.framework,
            status=status,
            original_error=scout_output.failures[0].error if scout_output.failures else "Initial test failures",
            root_cause=detective_output.root_cause if detective_output else "Identified software defects",
            evidence=detective_output.evidence if detective_output else [],
            affected_files=scout_output.affected_files,
            files_modified=list(modified_files),
            patch_summary="; ".join(patch_summaries) if patch_summaries else "Applied targeted patches",
            tests_before=tests_before,
            tests_after=tests_after,
            iterations=iterations,
            regressions=regressions,
            validation_result="VERIFIED" if status == "SUCCESS" else "UNRESOLVED",
            confidence="High" if (detective_output and detective_output.confidence > 0.8) else "Medium",
            remaining_issues=[f.test for f in latest_test.details.get("failures", [])] if (latest_test and latest_test.failed > 0 and latest_test.details) else []
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

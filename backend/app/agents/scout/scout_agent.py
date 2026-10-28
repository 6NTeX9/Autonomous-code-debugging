import logging
from typing import Optional, Dict, Any, List
from app.tools.tool_context import ToolContext
from app.tools import (
    list_files, read_file, search_code, get_file_metadata,
    detect_project_type, analyze_dependencies, run_tests,
    get_test_results, inspect_error_log
)
from app.schemas.schemas import ScoutOutput, TestFailure
from app.core.llm import LLMProvider

logger = logging.getLogger("debugging_agent.agents.scout")

SCOUT_SYSTEM_PROMPT = """You are AGENT 1: SCOUT (Repository & Error Analysis Agent).
Your role is to systematically inspect repository structures, identify frameworks, run test suites,
capture failures, extract stack traces, and isolate affected files and symbols.
You must always output strict structured JSON matching the ScoutOutput schema.
Do not speculate about solutions; focus exclusively on high-precision observation and factual evidence."""

class ScoutAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def run(self, ctx: ToolContext, project_name: str) -> ScoutOutput:
        ctx.current_agent = "SCOUT"
        await ctx.emit_event(
            "AGENT_STARTED",
            message="Scout Agent initiated: Analyzing repository structure and executing initial tests"
        )

        # 1. Inspect repository structure
        files = await list_files(ctx, ".")
        
        # 2. Detect project type and frameworks
        project_info = await detect_project_type(ctx)
        
        # 3. Analyze dependencies
        dependencies_info = await analyze_dependencies(ctx)
        deps_list = []
        if "production" in dependencies_info:
            deps_list.extend(list(dependencies_info["production"].keys()))
        if "python_requirements" in dependencies_info:
            deps_list.extend(dependencies_info["python_requirements"])

        await ctx.emit_event(
            "REPOSITORY_ANALYZED",
            payload={
                "project": project_name,
                "language": project_info.get("language"),
                "framework": project_info.get("framework"),
                "test_framework": project_info.get("test_framework"),
                "files_count": len(files)
            },
            message=f"Repository analyzed: {project_info.get('language')} project with {project_info.get('framework')}"
        )

        # 4. Run initial test suite to capture failures
        test_exec = await run_tests(ctx)
        test_summary = await get_test_results(ctx, test_exec)

        combined_error_log = f"{test_exec.stdout}\n{test_exec.stderr}".strip()
        parsed_errors = await inspect_error_log(ctx, combined_error_log)

        # 5. Identify affected source files & relevant symbols
        source_affected_files: List[str] = []
        relevant_symbols: List[str] = []

        # Parse from stack frames and referenced files in errors
        for ref in parsed_errors.get("referenced_files", []):
            fpath = ref.get("file", "")
            if fpath and not fpath.startswith("tests/") and not fpath.startswith("test/"):
                if fpath not in source_affected_files:
                    source_affected_files.append(fpath)

        # Extract symbols and search source files for matching symbols
        for fail in test_summary.failures:
            for candidate in [
                "getUser", "calculateDiscount", "calculateShipping", "userController", "discountService", "orderService",
                "renewSubscription", "calculateAnnualSavings", "isAccountActive", "subscriptionService"
            ]:
                if candidate.lower() in fail.test.lower() or candidate.lower() in fail.error.lower():
                    sym_label = candidate + "()" if not candidate.endswith("Service") and not candidate.endswith("Controller") else candidate
                    if sym_label not in relevant_symbols:
                        relevant_symbols.append(sym_label)
                    
                    matches = await search_code(ctx, candidate)
                    for m in matches:
                        m_file = m["file"]
                        if not m_file.startswith("tests/") and not m_file.startswith("test/") and m_file not in source_affected_files:
                            source_affected_files.append(m_file)

        # Fallback to source directory scan if still empty
        if not source_affected_files:
            for candidate_dir in ["src", "app", "lib"]:
                dir_path = ctx.workspace_path / candidate_dir
                if dir_path.is_dir():
                    for root, _, fs in os.walk(dir_path):
                        for f in fs:
                            if f.endswith((".ts", ".js", ".py")) and not f.endswith((".test.ts", ".spec.ts")):
                                rel = str(Path(root) / f).replace(str(ctx.workspace_path) + "/", "")
                                if rel not in source_affected_files:
                                    source_affected_files.append(rel)

        if test_summary.failed > 0:
            await ctx.emit_event(
                "ERROR_DETECTED",
                payload={
                    "total": test_summary.total,
                    "passed": test_summary.passed,
                    "failed": test_summary.failed,
                    "affected_files": source_affected_files,
                    "primary_error": test_summary.failures[0].error if test_summary.failures else "Test failure"
                },
                message=f"Detected {test_summary.failed} failing test(s). Primary failure: {test_summary.failures[0].test if test_summary.failures else 'Unknown'}"
            )

        scout_output = ScoutOutput(
            session_id=ctx.session_id,
            project=project_name,
            language=project_info.get("language", "Unknown"),
            framework=project_info.get("framework"),
            test_framework=project_info.get("test_framework"),
            source_dirs=project_info.get("source_dirs", []),
            test_dirs=project_info.get("test_dirs", []),
            entry_points=project_info.get("entry_points", []),
            dependencies=deps_list,
            initial_test_summary={
                "total": test_summary.total,
                "passed": test_summary.passed,
                "failed": test_summary.failed
            },
            failures=test_summary.failures,
            stack_trace=combined_error_log[:1500] if combined_error_log else None,
            affected_files=source_affected_files,
            relevant_symbols=relevant_symbols,
            raw_error_log=combined_error_log
        )

        await ctx.emit_event(
            "AGENT_COMPLETED",
            payload={"output": scout_output.model_dump()},
            message="Scout Agent completed repository analysis and failure detection."
        )

        return scout_output

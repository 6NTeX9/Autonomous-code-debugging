import json
import logging
from typing import Optional, Dict, Any, List
from app.tools.tool_context import ToolContext
from app.tools import (
    read_file, search_code, create_git_checkpoint,
    apply_patch, get_git_diff, rollback_changes
)
from app.schemas.schemas import DetectiveOutput, RepairerOutput
from app.core.llm import LLMProvider

logger = logging.getLogger("debugging_agent.agents.repairer")

REPAIRER_SYSTEM_PROMPT = """You are AGENT 3: REPAIRER (Fix Generation & Code Repair Agent).
Your mission is to formulate and apply the smallest safe patch to repair the verified root cause.
SAFETY RULES - STRICT ENFORCEMENT:
1. NEVER delete test files or test cases to make them pass.
2. NEVER modify expected test values or disable assertions.
3. NEVER comment out or bypass failing validation checks.
4. Make the minimal necessary change to fix the defect while preserving public API contracts.
5. Always preserve existing coding style and formatting conventions.
6. Checkpoint git state before any file modifications.
Output strict JSON with:
{
  "patch_id": "...",
  "modified_files": ["..."],
  "patch_summary": "...",
  "diff": "...",
  "file_contents": { "path/to/file": "full updated content" }  // optional direct replacement
}"""

class RepairerAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def run(
        self,
        ctx: ToolContext,
        detective_diagnosis: DetectiveOutput
    ) -> RepairerOutput:
        ctx.current_agent = "REPAIRER"
        await ctx.emit_event(
            "AGENT_STARTED",
            message=f"Repairer Agent initiated: Generating fix for iteration {ctx.iteration}"
        )

        # 1. Mandatory safety rule: Create Git checkpoint first
        checkpoint_name = await create_git_checkpoint(ctx, f"checkpoint_before_iteration_{ctx.iteration}")

        # 2. Read full contents of files identified for repair
        target_files_content = {}
        for target_file in detective_diagnosis.affected_files:
            try:
                content = await read_file(ctx, target_file)
                target_files_content[target_file] = content
            except Exception as e:
                logger.warning(f"Could not read target file {target_file}: {e}")

        # 3. Request LLM fix generation
        prompt_payload = {
            "iteration": ctx.iteration,
            "root_cause": detective_diagnosis.root_cause,
            "evidence": detective_diagnosis.evidence,
            "repair_strategy": detective_diagnosis.repair_strategy,
            "constraints": detective_diagnosis.constraints,
            "target_files": list(target_files_content.keys()),
            "files_content": target_files_content
        }

        user_prompt = f"Generate a minimal safe patch addressing this diagnosis strictly following safety rules:\n{json.dumps(prompt_payload, indent=2)}"

        raw_llm_response = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=REPAIRER_SYSTEM_PROMPT,
            json_mode=True,
            temperature=0.1
        )

        try:
            parsed = json.loads(raw_llm_response)
        except Exception:
            parsed = {
                "patch_id": f"patch_iter_{ctx.iteration}",
                "modified_files": detective_diagnosis.affected_files,
                "patch_summary": "Applied targeted code fix",
                "diff": ""
            }

        patch_id = parsed.get("patch_id", f"patch_{ctx.iteration}")
        modified_files = parsed.get("modified_files", detective_diagnosis.affected_files)
        patch_summary = parsed.get("patch_summary", "Targeted code fix")
        diff_str = parsed.get("diff", "")
        file_contents = parsed.get("file_contents", None)

        await ctx.emit_event(
            "PATCH_GENERATED",
            payload={
                "patch_id": patch_id,
                "modified_files": modified_files,
                "summary": patch_summary
            },
            message=f"Generated patch '{patch_id}': {patch_summary}"
        )

        # 4. Apply the patch
        patch_result = await apply_patch(
            ctx,
            patch_diff=diff_str,
            modified_files=modified_files,
            file_contents=file_contents
        )

        # 5. Capture actual git diff
        actual_diff = await get_git_diff(ctx, checkpoint_name)
        if not actual_diff and diff_str:
            actual_diff = diff_str

        output = RepairerOutput(
            session_id=ctx.session_id,
            iteration=ctx.iteration,
            patch_id=patch_id,
            modified_files=patch_result.get("applied_files", modified_files),
            diff=actual_diff,
            checkpoint=checkpoint_name,
            patch_summary=patch_summary
        )

        await ctx.emit_event(
            "AGENT_COMPLETED",
            payload={"output": output.model_dump()},
            message=f"Repairer Agent applied patch and generated diff ({len(actual_diff)} chars)."
        )

        return output

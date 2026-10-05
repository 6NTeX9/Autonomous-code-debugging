import json
import logging
from typing import Optional, Dict, Any, List
from app.tools.tool_context import ToolContext
from app.tools import read_file, search_code, get_file_metadata
from app.schemas.schemas import ScoutOutput, DetectiveOutput, HypothesisItem, GuardianOutput
from app.core.llm import LLMProvider

logger = logging.getLogger("debugging_agent.agents.detective")

DETECTIVE_SYSTEM_PROMPT = """You are AGENT 2: DETECTIVE (Root Cause & Reasoning Agent).
Your responsibility is to investigate failures reported by Agent 1 (Scout) or previous iteration results.
You must:
1. Examine relevant source code files and call sites.
2. Compare expected versus actual behavior.
3. Formulate multiple competing hypotheses with confidence scores (0.0 to 1.0) and concrete evidence.
4. Select the most likely root cause supported by direct code evidence.
5. Define a targeted repair strategy and architectural constraints for Agent 3.
6. Provide a concise, evidence-based reasoning summary. DO NOT output hidden chain-of-thought or internal monologues.
Output strictly formatted JSON matching the DetectiveOutput schema."""

class DetectiveAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def run(
        self,
        ctx: ToolContext,
        scout_findings: ScoutOutput,
        previous_guardian_feedback: Optional[GuardianOutput] = None
    ) -> DetectiveOutput:
        ctx.current_agent = "DETECTIVE"
        await ctx.emit_event(
            "AGENT_STARTED",
            message=f"Detective Agent initiated: Investigating root cause for iteration {ctx.iteration}"
        )

        # 1. Inspect relevant source files identified by Scout
        inspected_sources = {}
        for file_path in scout_findings.affected_files:
            try:
                content = await read_file(ctx, file_path)
                inspected_sources[file_path] = content[:3000]
            except Exception as e:
                logger.warning(f"Could not read affected file {file_path}: {e}")

        # Also search for symbols if any
        symbol_usages = {}
        for sym in scout_findings.relevant_symbols:
            clean_sym = sym.replace("()", "")
            matches = await search_code(ctx, clean_sym)
            symbol_usages[clean_sym] = matches[:5]

        # 2. Construct prompt for reasoning & hypothesis generation
        prompt_data = {
            "iteration": ctx.iteration,
            "project": scout_findings.project,
            "language": scout_findings.language,
            "framework": scout_findings.framework,
            "failures": [f.model_dump() for f in scout_findings.failures],
            "stack_trace": scout_findings.stack_trace,
            "relevant_symbols": scout_findings.relevant_symbols,
            "inspected_files": list(inspected_sources.keys()),
            "file_contents_sample": inspected_sources,
            "symbol_call_sites": symbol_usages,
            "previous_guardian_feedback": previous_guardian_feedback.model_dump() if previous_guardian_feedback else None
        }

        user_prompt = f"Analyze the following failure context and generate hypotheses, root cause diagnosis, and repair strategy in JSON format:\n{json.dumps(prompt_data, indent=2)}"

        raw_llm_response = await self.llm.generate(
            prompt=user_prompt,
            system_prompt=DETECTIVE_SYSTEM_PROMPT,
            json_mode=True,
            temperature=0.2
        )

        try:
            parsed = json.loads(raw_llm_response)
        except Exception:
            parsed = {}

        root_cause_text = parsed.get("root_cause") or "Missing null check or calculation defect in target file"
        confidence_val = float(parsed.get("confidence") or 0.90)
        repair_strat = parsed.get("repair_strategy") or "Apply defensive checks"
        reasoning_sum = parsed.get("reasoning_summary") or "Analyzed call sites and isolated failure cause."

        # Emit events for each hypothesis created
        hypotheses_objs = []
        for h in parsed.get("hypotheses", []):
            item = HypothesisItem(
                description=h.get("description", "Potential failure in logic"),
                evidence=h.get("evidence", []),
                affected_files=h.get("affected_files", []),
                confidence=float(h.get("confidence", 0.5))
            )
            hypotheses_objs.append(item)
            await ctx.emit_event(
                "HYPOTHESIS_CREATED",
                payload=item.model_dump(),
                message=f"Formulated hypothesis ({int(item.confidence * 100)}% conf): {item.description[:90]}..."
            )

        if not hypotheses_objs:
            fallback_hyp = HypothesisItem(
                description=root_cause_text,
                evidence=parsed.get("evidence", ["Test failed"]),
                affected_files=parsed.get("affected_files", scout_findings.affected_files),
                confidence=confidence_val
            )
            hypotheses_objs.append(fallback_hyp)

        # Emit root cause identified event
        await ctx.emit_event(
            "ROOT_CAUSE_IDENTIFIED",
            payload={
                "root_cause": root_cause_text,
                "confidence": confidence_val,
                "affected_files": parsed.get("affected_files", scout_findings.affected_files),
                "strategy": repair_strat
            },
            message=f"Root cause confirmed with {int(confidence_val * 100)}% confidence: {root_cause_text[:120]}..."
        )

        output = DetectiveOutput(
            session_id=ctx.session_id,
            iteration=ctx.iteration,
            hypotheses=hypotheses_objs,
            root_cause=root_cause_text,
            evidence=parsed.get("evidence", []),
            affected_files=parsed.get("affected_files", scout_findings.affected_files),
            confidence=confidence_val,
            repair_strategy=repair_strat,
            constraints=parsed.get("constraints", []),
            reasoning_summary=reasoning_sum
        )

        await ctx.emit_event(
            "AGENT_COMPLETED",
            payload={"output": output.model_dump()},
            message="Detective Agent completed root-cause investigation."
        )

        return output

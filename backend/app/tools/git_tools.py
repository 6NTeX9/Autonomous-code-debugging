import asyncio
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.tools.tool_context import ToolContext
from app.sandbox.security import validate_safe_path

logger = logging.getLogger("debugging_agent.tools.git")

async def _run_git_cmd(ctx: ToolContext, cmd: List[str]) -> str:
    proc = await asyncio.create_subprocess_exec(
        "git", *cmd,
        cwd=str(ctx.workspace_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err = stderr.decode('utf-8', errors='replace').strip()
        logger.warning(f"Git command {' '.join(cmd)} failed: {err}")
    return stdout.decode('utf-8', errors='replace').strip()

async def ensure_git_repo(ctx: ToolContext) -> None:
    git_dir = ctx.workspace_path / ".git"
    if not git_dir.exists():
        await _run_git_cmd(ctx, ["init"])
        await _run_git_cmd(ctx, ["config", "user.name", "Autonomous Debugger"])
        await _run_git_cmd(ctx, ["config", "user.email", "agent@autonomous-debugger.local"])
        await _run_git_cmd(ctx, ["add", "-A"])
        await _run_git_cmd(ctx, ["commit", "-m", "Initial repository state before debugging", "--allow-empty"])

async def create_git_checkpoint(ctx: ToolContext, label: Optional[str] = None) -> str:
    checkpoint_name = label or f"checkpoint_before_iteration_{ctx.iteration}"
    await ctx.emit_event("TOOL_CALL", tool="create_git_checkpoint", payload={"checkpoint": checkpoint_name})
    
    await ensure_git_repo(ctx)
    await _run_git_cmd(ctx, ["add", "-A"])
    await _run_git_cmd(ctx, ["commit", "-m", f"State before {checkpoint_name}", "--allow-empty"])
    
    # Create or update tag
    await _run_git_cmd(ctx, ["tag", "-f", checkpoint_name])
    
    # Get current commit hash
    commit_hash = await _run_git_cmd(ctx, ["rev-parse", "HEAD"])
    
    await ctx.emit_event(
        "TOOL_RESULT",
        tool="create_git_checkpoint",
        payload={"checkpoint": checkpoint_name, "commit": commit_hash},
        message=f"Git checkpoint '{checkpoint_name}' created at {commit_hash[:8]}"
    )
    return checkpoint_name

async def get_git_diff(ctx: ToolContext, checkpoint: Optional[str] = None) -> str:
    await ctx.emit_event("TOOL_CALL", tool="get_git_diff", payload={"checkpoint": checkpoint})
    await ensure_git_repo(ctx)

    if checkpoint:
        diff_output = await _run_git_cmd(ctx, ["diff", checkpoint, "HEAD"])
        # Also include uncommitted changes if any
        uncommitted = await _run_git_cmd(ctx, ["diff"])
        if uncommitted:
            diff_output = f"{diff_output}\n{uncommitted}".strip()
    else:
        diff_output = await _run_git_cmd(ctx, ["diff", "HEAD"])
        if not diff_output:
            diff_output = await _run_git_cmd(ctx, ["diff"])

    await ctx.emit_event(
        "TOOL_RESULT",
        tool="get_git_diff",
        payload={"diff_length": len(diff_output)}
    )
    return diff_output

def _apply_unified_diff(original_text: str, diff_text: str) -> str:
    """
    Applies a standard or unified diff chunk cleanly.
    Fallback: replace chunks based on @@ headers or simple search-and-replace.
    """
    lines = original_text.splitlines(keepends=True)
    diff_lines = diff_text.strip().splitlines()

    # If it's a standard patch chunk
    removals = []
    additions = []
    for dl in diff_lines:
        if dl.startswith("-") and not dl.startswith("---"):
            removals.append(dl[1:])
        elif dl.startswith("+") and not dl.startswith("+++"):
            additions.append(dl[1:])

    if removals and additions:
        old_block = "\n".join(removals)
        new_block = "\n".join(additions)
        orig_joined = "".join(lines)
        if old_block in orig_joined:
            return orig_joined.replace(old_block, new_block, 1)

    return original_text

async def apply_patch(
    ctx: ToolContext,
    patch_diff: str,
    modified_files: Optional[List[str]] = None,
    file_contents: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    await ctx.emit_event("TOOL_CALL", tool="apply_patch", payload={"modified_files": modified_files or []})
    await ensure_git_repo(ctx)

    success = False
    applied_files = []

    # If direct full file replacements are provided
    if file_contents:
        for rel_path, content in file_contents.items():
            target_path = validate_safe_path(rel_path, ctx.workspace_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            applied_files.append(rel_path)
        success = True

    # Otherwise apply patch via git apply or fallback
    if not success and patch_diff:
        # Try `git apply`
        proc = await asyncio.create_subprocess_exec(
            "git", "apply", "--ignore-whitespace", "--unidiff-zero", "-",
            cwd=str(ctx.workspace_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate(input=patch_diff.encode('utf-8'))
        if proc.returncode == 0:
            success = True
            if modified_files:
                applied_files.extend(modified_files)
        else:
            # Fallback chunk replacer for modified files
            logger.info("git apply failed, attempting line-level diff substitution...")
            if modified_files:
                for rel_path in modified_files:
                    try:
                        target_path = validate_safe_path(rel_path, ctx.workspace_path)
                        if target_path.exists():
                            orig = target_path.read_text(encoding="utf-8")
                            updated = _apply_unified_diff(orig, patch_diff)
                            if updated != orig:
                                target_path.write_text(updated, encoding="utf-8")
                                applied_files.append(rel_path)
                                success = True
                    except Exception as e:
                        logger.error(f"Fallback patch failed for {rel_path}: {e}")

    await ctx.emit_event(
        "PATCH_APPLIED",
        tool="apply_patch",
        payload={"applied_files": applied_files, "success": success},
        message=f"Applied patch to {len(applied_files)} file(s)"
    )

    return {
        "success": success,
        "applied_files": applied_files
    }

async def rollback_changes(ctx: ToolContext, checkpoint: Optional[str] = None) -> Dict[str, Any]:
    target = checkpoint or f"checkpoint_before_iteration_{ctx.iteration}"
    await ctx.emit_event("TOOL_CALL", tool="rollback_changes", payload={"target_checkpoint": target})
    
    await ensure_git_repo(ctx)
    await _run_git_cmd(ctx, ["reset", "--hard", target])
    await _run_git_cmd(ctx, ["clean", "-fd"])

    await ctx.emit_event(
        "ROLLBACK",
        tool="rollback_changes",
        payload={"target_checkpoint": target},
        message=f"Rolled back all modifications to checkpoint '{target}'"
    )
    return {"status": "ROLLED_BACK", "checkpoint": target}

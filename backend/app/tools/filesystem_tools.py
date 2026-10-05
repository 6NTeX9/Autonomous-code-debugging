import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.tools.tool_context import ToolContext
from app.sandbox.security import validate_safe_path

# Standard ignore patterns
IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".idea", ".vscode"}

async def list_files(ctx: ToolContext, rel_path: str = ".") -> List[Dict[str, Any]]:
    await ctx.emit_event("TOOL_CALL", tool="list_files", payload={"path": rel_path})
    target_dir = validate_safe_path(rel_path, ctx.workspace_path)

    results = []
    if not target_dir.exists():
        await ctx.emit_event("TOOL_RESULT", tool="list_files", payload={"error": "Directory not found"})
        return []

    for root, dirs, files in os.walk(target_dir):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            full_path = Path(root) / f
            try:
                rel = full_path.relative_to(ctx.workspace_path)
                stat = full_path.stat()
                results.append({
                    "path": str(rel),
                    "size": stat.st_size,
                    "is_dir": False
                })
            except Exception:
                continue

    await ctx.emit_event(
        "TOOL_RESULT",
        tool="list_files",
        payload={"count": len(results)},
        message=f"Discovered {len(results)} files in repository"
    )
    return results

async def read_file(
    ctx: ToolContext,
    rel_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> str:
    await ctx.emit_event("TOOL_CALL", tool="read_file", payload={"path": rel_path})
    target_file = validate_safe_path(rel_path, ctx.workspace_path)

    if not target_file.exists() or not target_file.is_file():
        err_msg = f"File {rel_path} does not exist"
        await ctx.emit_event("TOOL_RESULT", tool="read_file", payload={"error": err_msg})
        raise FileNotFoundError(err_msg)

    with open(target_file, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    if start_line is not None or end_line is not None:
        start = max(1, start_line or 1) - 1
        end = min(len(lines), end_line or len(lines))
        content = "".join(lines[start:end])
    else:
        content = "".join(lines)

    await ctx.emit_event(
        "TOOL_RESULT",
        tool="read_file",
        payload={"path": rel_path, "bytes": len(content.encode('utf-8'))},
        message=f"Read {len(content)} characters from {rel_path}"
    )
    return content

async def search_code(
    ctx: ToolContext,
    query: str,
    file_pattern: Optional[str] = None
) -> List[Dict[str, Any]]:
    await ctx.emit_event("TOOL_CALL", tool="search_code", payload={"query": query})
    results = []
    regex = re.compile(re.escape(query), re.IGNORECASE)

    for root, dirs, files in os.walk(ctx.workspace_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if file_pattern and not f.endswith(file_pattern.replace("*", "")):
                continue
            full_path = Path(root) / f
            try:
                rel = full_path.relative_to(ctx.workspace_path)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                    for line_no, line in enumerate(file_obj, 1):
                        if regex.search(line):
                            results.append({
                                "file": str(rel),
                                "line_number": line_no,
                                "line_content": line.strip()
                            })
            except Exception:
                continue

    await ctx.emit_event(
        "TOOL_RESULT",
        tool="search_code",
        payload={"query": query, "matches_count": len(results)},
        message=f"Found {len(results)} match(es) for '{query}'"
    )
    return results

async def get_file_metadata(ctx: ToolContext, rel_path: str) -> Dict[str, Any]:
    await ctx.emit_event("TOOL_CALL", tool="get_file_metadata", payload={"path": rel_path})
    target_file = validate_safe_path(rel_path, ctx.workspace_path)

    if not target_file.exists():
        return {"exists": False}

    stat = target_file.stat()
    lines_count = 0
    if target_file.is_file():
        try:
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                lines_count = sum(1 for _ in f)
        except Exception:
            pass

    metadata = {
        "exists": True,
        "path": rel_path,
        "size_bytes": stat.st_size,
        "lines": lines_count,
        "is_file": target_file.is_file(),
        "is_dir": target_file.is_dir(),
        "last_modified": stat.st_mtime
    }
    await ctx.emit_event("TOOL_RESULT", tool="get_file_metadata", payload=metadata)
    return metadata

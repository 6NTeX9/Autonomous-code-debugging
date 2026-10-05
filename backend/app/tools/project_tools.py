import json
from pathlib import Path
from typing import Dict, Any, List
from app.tools.tool_context import ToolContext

async def detect_project_type(ctx: ToolContext) -> Dict[str, Any]:
    await ctx.emit_event("TOOL_CALL", tool="detect_project_type")
    
    ws = ctx.workspace_path
    language = "Unknown"
    framework = "Unknown"
    test_framework = "Unknown"
    source_dirs = []
    test_dirs = []
    entry_points = []

    # Check for Node / TS / JS
    package_json_path = ws / "package.json"
    tsconfig_path = ws / "tsconfig.json"
    requirements_path = ws / "requirements.txt"
    pyproject_path = ws / "pyproject.toml"
    pom_path = ws / "pom.xml"

    if tsconfig_path.exists() or list(ws.glob("**/*.ts")):
        language = "TypeScript"
    elif package_json_path.exists() or list(ws.glob("**/*.js")):
        language = "JavaScript"
    elif requirements_path.exists() or pyproject_path.exists() or list(ws.glob("**/*.py")):
        language = "Python"
    elif pom_path.exists() or list(ws.glob("**/*.java")):
        language = "Java"

    # Analyze package.json if present
    if package_json_path.exists():
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
            deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}

            if "express" in deps:
                framework = "Express"
            elif "@nestjs/core" in deps:
                framework = "NestJS"
            elif "fastify" in deps:
                framework = "Fastify"

            if "jest" in deps or "ts-jest" in deps:
                test_framework = "Jest"
            elif "vitest" in deps:
                test_framework = "Vitest"
            elif "mocha" in deps:
                test_framework = "Mocha"
        except Exception:
            pass

    # Python framework detection
    if language == "Python":
        test_framework = "Pytest"
        if requirements_path.exists():
            try:
                content = requirements_path.read_text(encoding="utf-8")
                if "fastapi" in content:
                    framework = "FastAPI"
                elif "django" in content:
                    framework = "Django"
                elif "flask" in content:
                    framework = "Flask"
            except Exception:
                pass

    # Identify directories
    for candidate in ["src", "app", "lib"]:
        if (ws / candidate).is_dir():
            source_dirs.append(candidate)

    for candidate in ["tests", "test", "__tests__", "spec"]:
        if (ws / candidate).is_dir():
            test_dirs.append(candidate)

    # Identify entry points
    for candidate in [
        "src/index.ts", "src/app.ts", "src/server.ts",
        "index.ts", "app.ts", "server.ts",
        "src/index.js", "src/app.js", "src/server.js",
        "index.js", "app.js", "server.js",
        "main.py", "app.py", "src/main.py", "src/app.py"
    ]:
        if (ws / candidate).exists():
            entry_points.append(candidate)

    summary = {
        "language": language,
        "framework": framework,
        "test_framework": test_framework,
        "source_dirs": source_dirs,
        "test_dirs": test_dirs,
        "entry_points": entry_points
    }

    await ctx.emit_event(
        "TOOL_RESULT",
        tool="detect_project_type",
        payload=summary,
        message=f"Detected {language} project using {framework} and {test_framework}"
    )
    return summary

async def analyze_dependencies(ctx: ToolContext) -> Dict[str, Any]:
    await ctx.emit_event("TOOL_CALL", tool="analyze_dependencies")
    ws = ctx.workspace_path
    deps = {}

    pkg_path = ws / "package.json"
    if pkg_path.exists():
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            deps["production"] = data.get("dependencies", {})
            deps["development"] = data.get("devDependencies", {})
        except Exception as e:
            deps["error"] = str(e)

    req_path = ws / "requirements.txt"
    if req_path.exists():
        try:
            lines = [line.strip() for line in req_path.read_text().splitlines() if line.strip() and not line.startswith("#")]
            deps["python_requirements"] = lines
        except Exception as e:
            deps["error"] = str(e)

    await ctx.emit_event(
        "TOOL_RESULT",
        tool="analyze_dependencies",
        payload={"dependency_summary": deps}
    )
    return deps

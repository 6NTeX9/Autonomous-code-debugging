import shutil
import uuid
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.core.config import settings
from app.models.database_models import Project
from app.sandbox.security import safe_extract_zip

class ProjectService:
    @staticmethod
    async def create_project_from_upload(
        db: Session,
        name: str,
        upload_file: UploadFile,
        description: Optional[str] = None
    ) -> Project:
        project_id = str(uuid.uuid4())
        workspace_path = settings.WORKSPACES_DIR / project_id
        workspace_path.mkdir(parents=True, exist_ok=True)

        temp_zip = workspace_path / "upload.zip"
        with open(temp_zip, "wb") as f:
            content = await upload_file.read()
            f.write(content)

        # Extract safely with anti-ZipSlip and anti-ZipBomb protection
        safe_extract_zip(temp_zip, workspace_path)
        temp_zip.unlink(missing_ok=True)

        # If uploaded project has package.json, link sample project's node_modules so npm test works immediately
        source_modules = settings.SAMPLE_PROJECT_DIR / "node_modules"
        if (workspace_path / "package.json").exists() and source_modules.exists() and not (workspace_path / "node_modules").exists():
            try:
                (workspace_path / "node_modules").symlink_to(source_modules.resolve(), target_is_directory=True)
            except Exception:
                pass

        project = Project(
            id=project_id,
            name=name,
            description=description or f"Uploaded repository: {name}",
            workspace_path=str(workspace_path)
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def create_project_from_sample(db: Session, sample_dir: Optional[Path] = None) -> Project:
        project_id = str(uuid.uuid4())
        workspace_path = settings.WORKSPACES_DIR / project_id
        workspace_path.mkdir(parents=True, exist_ok=True)

        source_dir = sample_dir or settings.SAMPLE_PROJECT_DIR
        if not source_dir.exists():
            raise FileNotFoundError(f"Sample project directory not found at {source_dir}")

        # Copy sample project files (ignoring node_modules if present to keep it fast)
        def ignore_patterns(folder, contents):
            ignored = set()
            if "node_modules" in contents:
                ignored.add("node_modules")
            if ".git" in contents:
                ignored.add(".git")
            return ignored

        shutil.copytree(source_dir, workspace_path, dirs_exist_ok=True, ignore=ignore_patterns)

        # If sample project has package.json and the source node_modules exists, symlink or copy node_modules
        source_modules = source_dir / "node_modules"
        if source_modules.exists() and not (workspace_path / "node_modules").exists():
            try:
                (workspace_path / "node_modules").symlink_to(source_modules.resolve(), target_is_directory=True)
            except Exception:
                pass

        project = Project(
            id=project_id,
            name="sample-buggy-project",
            description="E-commerce & Order Management Service with intentional realistic defects",
            language="TypeScript",
            framework="Express",
            test_framework="Jest",
            workspace_path=str(workspace_path)
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

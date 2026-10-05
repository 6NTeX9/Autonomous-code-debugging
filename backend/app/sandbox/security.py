import os
import zipfile
from pathlib import Path
from typing import Set

class SecurityViolationError(Exception):
    pass

def validate_safe_path(target_path: str, base_dir: Path) -> Path:
    """
    Ensure target_path resolves strictly within base_dir.
    Prevents path traversal attacks (e.g., ../../../etc/passwd).
    """
    base_resolved = base_dir.resolve()
    target_resolved = (base_dir / target_path).resolve() if not os.path.isabs(target_path) else Path(target_path).resolve()

    try:
        target_resolved.relative_to(base_resolved)
    except ValueError:
        raise SecurityViolationError(
            f"Path traversal detected! Target path '{target_path}' resolves to '{target_resolved}', outside '{base_resolved}'"
        )
    return target_resolved

def safe_extract_zip(zip_path: Path, destination_dir: Path, max_uncompressed_bytes: int = 50 * 1024 * 1024) -> None:
    """
    Safely extract a ZIP archive while protecting against:
    - Zip Slip (path traversal in entry names)
    - Zip Bombs (excessive uncompressed size)
    - Symlink / device attacks
    """
    destination_dir = destination_dir.resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    
    total_extracted_bytes = 0

    with zipfile.ZipFile(zip_path, 'r') as archive:
        for member in archive.infolist():
            # Check for zip bomb
            total_extracted_bytes += member.file_size
            if total_extracted_bytes > max_uncompressed_bytes:
                raise SecurityViolationError(
                    f"ZIP bomb detected! Archive exceeds maximum allowed uncompressed size ({max_uncompressed_bytes} bytes)"
                )

            # Prevent absolute path or path traversal in filenames
            filename = member.filename
            if os.path.isabs(filename) or ".." in filename.split("/"):
                raise SecurityViolationError(f"Malicious zip entry detected: {filename}")

            target_path = (destination_dir / filename).resolve()
            try:
                target_path.relative_to(destination_dir)
            except ValueError:
                raise SecurityViolationError(f"ZipSlip vulnerability prevented for entry: {filename}")

            # Do not extract symlinks or special devices
            mode = member.external_attr >> 16
            if mode & 0o120000 == 0o120000:
                # Symlink - skip for security
                continue

            archive.extract(member, destination_dir)

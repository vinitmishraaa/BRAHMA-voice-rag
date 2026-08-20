from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def create_metadata(file_path: str | Path, text: str) -> dict:
    """
    Create metadata for an ingested document.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return {
        "document_id": str(uuid4()),
        "file_name": path.name,
        "file_type": path.suffix.lower(),
        "file_path": str(path.resolve()),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "character_count": len(text),
    }
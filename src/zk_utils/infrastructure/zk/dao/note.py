from pathlib import Path

from ...._base_models import BaseModel


class Note(BaseModel):
    title: str
    path: Path
    tags: list[str]
    content: str | None = None

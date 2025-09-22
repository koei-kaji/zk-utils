from pathlib import Path
from typing import Optional

from .._abc import Entity


class Note(Entity):
    title: str
    path: Path
    tags: list[str]
    content: Optional[str] = None

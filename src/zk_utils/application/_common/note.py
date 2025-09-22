from pathlib import Path

from ..._base_models import BaseFrozenModel


class Note(BaseFrozenModel):
    title: str
    path: Path
    tags: list[str]

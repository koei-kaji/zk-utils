from pathlib import Path
from typing import Annotated

from pydantic import PlainSerializer, WithJsonSchema

from ..._base_models import BaseFrozenModel


class Note(BaseFrozenModel):
    title: str
    path: Annotated[
        Path,
        PlainSerializer(str, return_type=str, when_used="json"),
        WithJsonSchema({"type": "string"}),
    ]
    tags: list[str]

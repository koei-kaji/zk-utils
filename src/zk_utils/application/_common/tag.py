from ..._base_models import BaseFrozenModel


class Tag(BaseFrozenModel):
    name: str
    note_count: int

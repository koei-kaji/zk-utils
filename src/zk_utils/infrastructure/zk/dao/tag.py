from ...._base_models import BaseModel


class Tag(BaseModel):
    name: str
    note_count: int

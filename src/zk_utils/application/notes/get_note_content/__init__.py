from pathlib import Path

from injector import inject, singleton

from ....domain.models.notes.if_note_repository import IFNoteRepository
from ..._abc import ABCInput, ABCOutput, ABCService


class GetNoteContentInput(ABCInput):
    path: Path


class GetNoteContentOutput(ABCOutput):
    content: str


@singleton
class GetNoteContentService(ABCService):
    _repository: IFNoteRepository

    @inject
    def __init__(self, repository: IFNoteRepository) -> None:
        super().__init__()
        self._repository = repository

    def handle(self, input_data: GetNoteContentInput) -> GetNoteContentOutput:
        note = self._repository.find_note_content(input_data.path)

        return GetNoteContentOutput(content=note.content)

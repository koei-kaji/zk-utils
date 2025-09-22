from pathlib import Path

from injector import inject, singleton

from ....domain.models.notes import IFNoteRepository
from ..._abc import ABCInput, ABCOutput, ABCService
from ..._common.note import Note


class CreateNoteInput(ABCInput):
    title: str
    path: Path


class CreateNoteOutput(ABCOutput):
    note: Note


@singleton
class CreateNoteService(ABCService):
    _repository: IFNoteRepository

    @inject
    def __init__(self, repository: IFNoteRepository) -> None:
        super().__init__()
        self._repository = repository

    def handle(self, input_data: CreateNoteInput) -> CreateNoteOutput:
        result = self._repository.create_note(input_data.title, input_data.path)

        return CreateNoteOutput(
            note=Note(title=result.title, path=result.path, tags=result.tags)
        )

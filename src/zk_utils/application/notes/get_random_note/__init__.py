from injector import inject, singleton

from ....domain.models.notes.if_note_repository import IFNoteRepository
from ..._abc import ABCInput, ABCOutput, ABCService
from ..._common.note import Note


class GetRandomNoteInput(ABCInput): ...


class GetRandomNoteOutput(ABCOutput):
    note: Note


@singleton
class GetRandomNoteService(ABCService[GetRandomNoteInput, GetRandomNoteOutput]):
    _repository: IFNoteRepository

    @inject
    def __init__(self, repository: IFNoteRepository) -> None:
        super().__init__()
        self._repository = repository

    def handle(self, input_data: GetRandomNoteInput) -> GetRandomNoteOutput:
        note = self._repository.find_random_note()

        return GetRandomNoteOutput(
            note=Note(title=note.title, path=note.path, tags=note.tags)
        )

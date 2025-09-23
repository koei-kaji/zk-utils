from injector import inject, singleton

from ....domain.models.notes.if_note_repository import IFNoteRepository
from ..._abc import ABCInput, ABCOutput, ABCService
from ..._common.note import Note


class GetLastModifiedNoteInput(ABCInput): ...


class GetLastModifiedNoteOutput(ABCOutput):
    note: Note


@singleton
class GetLastModifiedNoteService(
    ABCService[GetLastModifiedNoteInput, GetLastModifiedNoteOutput]
):
    _repository: IFNoteRepository

    @inject
    def __init__(self, repository: IFNoteRepository) -> None:
        super().__init__()
        self._repository = repository

    def handle(self, input_data: GetLastModifiedNoteInput) -> GetLastModifiedNoteOutput:
        note = self._repository.find_last_modified_note()

        return GetLastModifiedNoteOutput(
            note=Note(title=note.title, path=note.path, tags=note.tags)
        )

from injector import inject, singleton

from ....domain.models.notes.if_note_repository import IFNoteRepository
from ..._abc import ABCInput, ABCOutput, ABCService
from ..._common.note import Note


class GetTaglessNotesInput(ABCInput): ...


class GetTaglessNotesOutput(ABCOutput):
    notes: list[Note]


@singleton
class GetTaglessNotesService(ABCService[GetTaglessNotesInput, GetTaglessNotesOutput]):
    _repository: IFNoteRepository

    @inject
    def __init__(self, repository: IFNoteRepository) -> None:
        super().__init__()
        self._repository = repository

    def handle(self, input_data: GetTaglessNotesInput) -> GetTaglessNotesOutput:
        results = self._repository.find_tagless_notes()

        notes: list[Note] = []
        for result in results:
            note = Note(title=result.title, path=result.path, tags=result.tags)
            notes.append(note)

        return GetTaglessNotesOutput(notes=notes)

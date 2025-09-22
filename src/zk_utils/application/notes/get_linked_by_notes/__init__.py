from pathlib import Path

from injector import inject, singleton

from ..._abc import ABCInput, ABCOutput, ABCService
from ..._common.note import Note
from ..._common.pagination import Pagination
from ..if_note_query_service import IFNoteQueryService


class GetLinkedByNotesInput(ABCInput):
    page: int = 1
    per_page: int = 10
    path: Path


class GetLinkedByNotesOutput(ABCOutput):
    pagination: Pagination
    notes: list[Note]


@singleton
class GetLinkedByNotesService(
    ABCService[GetLinkedByNotesInput, GetLinkedByNotesOutput]
):
    _query_service: IFNoteQueryService

    @inject
    def __init__(self, query_service: IFNoteQueryService) -> None:
        super().__init__()
        self._query_service = query_service

    def handle(self, input_data: GetLinkedByNotesInput) -> GetLinkedByNotesOutput:
        return self._query_service.get_linked_by_notes(input_data)

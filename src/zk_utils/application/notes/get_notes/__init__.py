from typing import Literal

from injector import inject, singleton

from ..._abc import ABCInput, ABCOutput, ABCService
from ..._common.note import Note
from ..._common.pagination import Pagination
from ..if_note_query_service import IFNoteQueryService


class GetNotesInput(ABCInput):
    page: int = 1
    per_page: int = 10
    title_patterns: list[str]
    title_match_mode: Literal["AND", "OR"] = "AND"
    search_patterns: list[str]
    search_match_mode: Literal["AND", "OR"] = "AND"
    tags: list[str]
    tags_match_mode: Literal["AND", "OR"] = "AND"


class GetNotesOutput(ABCOutput):
    pagination: Pagination
    notes: list[Note]


@singleton
class GetNotesService(ABCService):
    _query_service: IFNoteQueryService

    @inject
    def __init__(self, query_service: IFNoteQueryService) -> None:
        super().__init__()
        self._query_service = query_service

    def handle(self, input_data: GetNotesInput) -> GetNotesOutput:
        return self._query_service.get_notes(input_data)

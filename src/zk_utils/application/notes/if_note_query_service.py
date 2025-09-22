import abc
from typing import TYPE_CHECKING

from .._abc import IFQueryService

if TYPE_CHECKING:
    from .get_link_to_notes import GetLinkToNotesInput, GetLinkToNotesOutput
    from .get_linked_by_notes import GetLinkedByNotesInput, GetLinkedByNotesOutput
    from .get_notes import GetNotesInput, GetNotesOutput
    from .get_related_notes import GetRelatedNotesInput, GetRelatedNotesOutput


class IFNoteQueryService(IFQueryService):
    @abc.abstractmethod
    def get_notes(self, input_data: "GetNotesInput") -> "GetNotesOutput": ...

    @abc.abstractmethod
    def get_link_to_notes(
        self, input_data: "GetLinkToNotesInput"
    ) -> "GetLinkToNotesOutput": ...

    @abc.abstractmethod
    def get_linked_by_notes(
        self, input_data: "GetLinkedByNotesInput"
    ) -> "GetLinkedByNotesOutput": ...

    @abc.abstractmethod
    def get_related_notes(
        self, input_data: "GetRelatedNotesInput"
    ) -> "GetRelatedNotesOutput": ...
